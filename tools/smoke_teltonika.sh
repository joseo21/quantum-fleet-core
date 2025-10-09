#!/usr/bin/env bash
set -euo pipefail

# ===========================
# Config (variables overrideables por env)
# ===========================
IMEI="${IMEI:-356307042123456}"
TENANT_NAME="${TENANT_NAME:-smoke-tenant}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-5027}"
API_BASE="${API_BASE:-http://localhost:8000}"
LAT="${LAT:--33.41}"
LON="${LON:--70.61}"
SPEED="${SPEED:-18.5}"
COUNT="${COUNT:-3}"
SIM="${SIM:-tools/sim_fmc650.py}"

# Servicio de Postgres en docker compose
PG_SVC="${PG_SVC:-postgres}"
# Estos se leen dentro del contenedor de Postgres
PG_USER_ENV="${PG_USER_ENV:-POSTGRES_USER}"
PG_DB_ENV="${PG_DB_ENV:-POSTGRES_DB}"

die(){ echo "✗ $*" >&2; exit 1; }
ok(){  echo "✓ $*"; }
_have(){ command -v "$1" >/dev/null 2>&1; }

# docker compose vs docker-compose
if _have docker && docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif _have docker-compose; then
  DC="docker-compose"
else
  die "No encuentro docker compose."
fi

_have curl   || die "curl no está instalado"
_have jq     || die "jq no está instalado (sudo apt-get install -y jq)"
_have python3 || die "python3 no está instalado"

# ===========================
# 1) API vivo
# ===========================
if curl -fsS -m 5 "$API_BASE/ingest/teltonika/ping" >/dev/null; then
  ok "API vivo: $API_BASE"
else
  curl -fsS -m 5 "$API_BASE/openapi.json" >/dev/null || die "API no responde en $API_BASE"
  ok "API vivo (por openapi.json): $API_BASE"
fi

# ===========================
# 2) Puerto TCP en escucha
# ===========================
if timeout 2 bash -lc "exec 3<>/dev/tcp/$HOST/$PORT" 2>/dev/null; then
  ok "TCP $HOST:$PORT accesible"
  exec 3>&- || true
else
  die "No puedo conectar a $HOST:$PORT"
fi

# ===========================
# 3) Asegurar TENANT y DEVICE en DB (vía psql con variables -v)
# ===========================
echo "→ Asegurando tenant '$TENANT_NAME' y device IMEI=$IMEI en DB…"
# Detectar user y db reales dentro del contenedor
read -r PG_USER PG_DB < <($DC exec -T "$PG_SVC" sh -lc 'echo "${'"$PG_USER_ENV"':-quantum} ${'"$PG_DB_ENV"':-quantumfleet}"')
[[ -n "$PG_USER" && -n "$PG_DB" ]] || die "No pude leer $PG_USER_ENV/$PG_DB_ENV dentro del contenedor $PG_SVC."

# **IMPORTANTE**: pasamos -v TENANT_NAME y -v IMEI y dentro del SQL usamos :'TENANT_NAME' y :'IMEI'
$DC exec -T "$PG_SVC" sh -lc \
"psql -v ON_ERROR_STOP=1 -U \"$PG_USER\" -d \"$PG_DB\" -v TENANT_NAME=\"$TENANT_NAME\" -v IMEI=\"$IMEI\" -f /dev/stdin" <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'tenants'
  ) THEN
    CREATE TABLE public.tenants (
      id   SERIAL PRIMARY KEY,
      name VARCHAR(120) UNIQUE
    );
  END IF;
END $$;

-- Upsert del tenant por nombre
INSERT INTO public.tenants(name) VALUES (:'TENANT_NAME')
ON CONFLICT (name) DO NOTHING;

-- Vincular/crear device con ese tenant
WITH t AS (
  SELECT id FROM public.tenants WHERE name = :'TENANT_NAME'
)
INSERT INTO public.devices(tenant_id, name, external_id)
SELECT t.id, 'FMC650 smoke', :'IMEI'
FROM t
ON CONFLICT (external_id)
DO UPDATE SET tenant_id = EXCLUDED.tenant_id, name = EXCLUDED.name;
SQL

# Obtener ids y corroborar asociación
DUMP_JSON="$($DC exec -T "$PG_SVC" sh -lc \
"psql -tA -U \"$PG_USER\" -d \"$PG_DB\" -F ',' -c \
\"SELECT d.id, COALESCE(d.tenant_id,0), COALESCE(t.name,'') 
   FROM devices d LEFT JOIN tenants t ON t.id=d.tenant_id 
  WHERE d.external_id='$IMEI' LIMIT 1;\" \
| awk -F',' '{printf(\"{\\\"device_id\\\":%s,\\\"tenant_id\\\":%s,\\\"tenant_name\\\":\\\"%s\\\"}\\n\",\$1,\$2,\$3)}'")"

DEVICE_ID=$(echo "$DUMP_JSON" | jq -r '.device_id')
DEVICE_TENANT_ID=$(echo "$DUMP_JSON" | jq -r '.tenant_id')
DEVICE_TENANT_NAME=$(echo "$DUMP_JSON" | jq -r '.tenant_name')

[[ "$DEVICE_ID" != "null" && -n "$DEVICE_ID" ]] || die "No encontré/creé el device para IMEI=$IMEI"
[[ "$DEVICE_TENANT_NAME" == "$TENANT_NAME" ]] || die "El device no quedó asociado al tenant '$TENANT_NAME' (tenía: '$DEVICE_TENANT_NAME')"
ok "Device $DEVICE_ID asociado al tenant '$DEVICE_TENANT_NAME'"

# ===========================
# 4) Enviar simulador y verificar ACKs
# ===========================
[[ -f "$SIM" ]] || die "No encuentro el simulador en $SIM"
echo "→ Simulando $COUNT puntos: IMEI=$IMEI ($LAT,$LON @ $SPEED)"
SIM_OUT="$(python3 "$SIM" --host "$HOST" --port "$PORT" --imei "$IMEI" \
          --lat "$LAT" --lon "$LON" --speed "$SPEED" --count "$COUNT" 2>&1 || true)"
echo "$SIM_OUT" | sed 's/^/  sim: /'

ACKS_OK=$(echo "$SIM_OUT" | grep -c 'ACK: 1' || true)
[[ "$ACKS_OK" -ge "$COUNT" ]] || die "ACKs OK ($ACKS_OK) < COUNT ($COUNT)"
ok "ACKs correctos ($ACKS_OK/$COUNT)"

# ===========================
# 5) Validar por API que llegó telemetría
# ===========================
sleep 1
RESP="$(curl -fsS "$API_BASE/telemetry/query?external_id=$IMEI&limit=$COUNT")" || die "Falla al consultar /telemetry/query"
LEN=$(echo "$RESP" | jq 'length')
[[ "$LEN" -ge 1 ]] || die "Sin registros devueltos por API (len=$LEN)"
HAS_GPS=$(echo "$RESP" | jq 'map(has("gps")) | all')
[[ "$HAS_GPS" == "true" ]] || die "La respuesta API no contiene campo gps en todos los elementos"
LAST=$(echo "$RESP" | jq '.[0] | {ts: .ts, lat: .gps.lat, lon: .gps.lon, speed: .gps.speed}')
ok "Telemetría por API OK. Último punto:"
echo "$LAST" | jq .

# ===========================
# 6) Validar en DB que la telemetría quedó con el tenant correcto
# ===========================
SQL_CHECK="
WITH d AS (SELECT id, tenant_id FROM devices WHERE external_id='$IMEI' LIMIT 1)
SELECT COUNT(*) 
FROM telemetry t, d 
WHERE t.device_id=d.id 
  AND COALESCE(t.tenant_id, d.tenant_id) = d.tenant_id
  AND t.ts > now() - interval '5 minutes';
"
OK_ROWS="$($DC exec -T "$PG_SVC" sh -lc \
"psql -tA -U \"$PG_USER\" -d \"$PG_DB\" -c \"$SQL_CHECK\" 2>/dev/null | tr -d '[:space:]'")"

[[ "$OK_ROWS" =~ ^[0-9]+$ ]] || die "No pude validar tenant en DB"
[[ "$OK_ROWS" -ge 1 ]] || die "La telemetría reciente no está guardando tenant_id correctamente"

ok "Tenant en telemetría validado ($OK_ROWS filas recientes con tenant esperado)"

echo
ok "SMOKE TEST COMPLETO 🎉"
