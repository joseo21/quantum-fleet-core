#!/usr/bin/env bash
set -euo pipefail

API=${API:-http://localhost:8000}
PG_USER=${POSTGRES_USER:-quantum}
PG_DB=${POSTGRES_DB:-quantumfleet}
TENANT_NAME=${TENANT_NAME:-smoke-tenant}
IMEI=${IMEI:-356307042123456}
TOKEN=${TOKEN:-token-webhook-123}

echo "✓ API vivo: $API"
curl -fsS "$API/health" >/dev/null || true

echo "→ Asegurando tenant y device en DB (sin DO $$, con name NOT NULL)…"
docker compose exec -T postgres sh -lc \
"psql -v ON_ERROR_STOP=1 -U \"$PG_USER\" -d \"$PG_DB\"" <<SQL
-- 1) Tenant por nombre (idempotente)
INSERT INTO public.tenants (name)
VALUES ('${TENANT_NAME}')
ON CONFLICT (name) DO NOTHING;

-- 2) Device por external_id (IMEI) con NAME SIEMPRE NO NULO
--    Si ya existe, conservamos su name actual; si está vacío o null, lo reemplazamos
INSERT INTO public.devices (tenant_id, name, external_id)
SELECT
  (SELECT id FROM public.tenants WHERE name='${TENANT_NAME}') AS tenant_id,
  COALESCE( (SELECT NULLIF(name, '') FROM public.devices WHERE external_id='${IMEI}'),
            'smoke-device ${IMEI}') AS name,
  '${IMEI}' AS external_id
ON CONFLICT (external_id) DO UPDATE
SET tenant_id = EXCLUDED.tenant_id,
    name      = COALESCE(public.devices.name, EXCLUDED.name);
SQL

echo "→ Crear/upsert conector con webhook + mapping…"
RESP=$(curl -sS -X POST "$API/connectors" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\":\"sensor-wh\",
    \"auth_type\":\"none\",
    \"webhook_token\":\"$TOKEN\",
    \"mapping\":{
      \"emit_telemetry\":true,
      \"external_id_path\":\"device.imei\",
      \"ts_path\":\"timestamp_ms\",
      \"gps_lat_path\":\"location.lat\",
      \"gps_lon_path\":\"location.lon\",
      \"gps_speed_path\":\"speed\"
    }
  }")
echo "$RESP" | jq .
CONNECTOR_ID=$(echo "$RESP" | jq -r .id)
echo "   connector_id=$CONNECTOR_ID"

echo "→ Disparando webhook /hooks/$TOKEN…"
TS_MS=$(( $(date +%s) * 1000 ))
curl -sS -X POST "$API/hooks/$TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"device\":{\"imei\":\"$IMEI\"},
    \"timestamp_ms\": $TS_MS,
    \"location\":{\"lat\":-33.41,\"lon\":-70.69},
    \"speed\": 18.5
  }" | jq .

echo "→ Consultando telemetría…"
curl -sS "$API/telemetry/query?external_id=$IMEI&limit=3" | jq .

echo "→ Últimos logs de connector_logs:"
docker compose exec -T postgres sh -lc \
'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -A -F"|" -c "SELECT id,at,direction,status,method,path FROM connector_logs ORDER BY id DESC LIMIT 10;"'
