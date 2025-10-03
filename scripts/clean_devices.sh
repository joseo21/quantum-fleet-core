#!/usr/bin/env bash
# scripts/clean_devices.sh
# Borra devices del tenant que NO estén referenciados por los panels del dashboard.
# Robusto ante respuestas vacías / no-JSON y sin cierres inesperados.

set -euo pipefail

API="${API:-http://localhost:8000}"
TENANT="${TENANT:-1}"
DID="${DID:-3}"        # Dashboard "Operación Planta" por defecto

echo "→ API=$API  TENANT=$TENANT  DID=$DID"

# 0) Asegurar TOKEN (si no está exportado)
if [ -z "${TOKEN:-}" ]; then
  TOKEN=$(
    curl -s -X POST "$API/auth/login" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      --data "username=admin@example.com&password=Admin123!" \
    | python3 - <<'PY'
import sys, json
try:
  d=json.load(sys.stdin)
  print(d.get("access_token",""))
except Exception:
  print("")
PY
  )
  if [ -z "$TOKEN" ]; then
    echo "❌ No pude obtener TOKEN (login). Revisa 'docker compose logs --tail=200 api'"
    exit 1
  fi
fi

# 1) Obtener dashboard y extraer device_id de cada panel.config (si existiera)
DASH_RAW="$(curl -s -H "Authorization: Bearer $TOKEN" "$API/tenants/$TENANT/dashboards/$DID" || true)"

REF_IDS=$(
  python3 - <<'PY'
import sys, json
raw = sys.stdin.read().strip()
ids=set()
if raw:
  try:
    d=json.loads(raw)
    for p in d.get("panels", []):
      cfg = p.get("config") or {}
      did = cfg.get("device_id")
      if isinstance(did, int):
        ids.add(str(did))
  except Exception:
    pass
print(" ".join(sorted(ids, key=lambda x: (len(x), x))))
PY
<<<"$DASH_RAW"
)

if [ -z "${REF_IDS:-}" ]; then
  echo "⚠️  Ningún panel referencia device_id en el dashboard DID=$DID."
fi

# 2) Armar lista de IDs a mantener (KEEP): los referenciados + 1 + DEVICE_ID (si existe)
KEEP_IDS=$(
  python3 - <<PY
import os, sys
items=set()
ref = os.environ.get("REF_IDS","").strip()
if ref:
  items.update(ref.split())
dev = os.environ.get("DEVICE_ID","").strip()
if dev:
  items.add(dev)
items.add("1")  # fallback
# Devolver ordenado numéricamente
print(" ".join(sorted(items, key=lambda x: int(x) if x.isdigit() else 10**9)))
PY
)
echo "→ Device IDs a mantener: ${KEEP_IDS:-<vacío>}"

# 3) Listar devices del tenant
DEVICES_RAW="$(curl -s -H "Authorization: Bearer $TOKEN" -H "X-Tenant-ID: $TENANT" "$API/devices" || true)"
if [ -z "$DEVICES_RAW" ]; then
  echo "ℹ️  /devices devolvió vacío. Nada que borrar."
  exit 0
fi

# 4) Borrar los NO referenciados (robusto ante errores/204/no-json)
echo "$DEVICES_RAW" | python3 - "$API" "$TOKEN" "$TENANT" "$KEEP_IDS" <<'PY'
import sys, json, urllib.request, urllib.error

API, TOKEN, TENANT, KEEP = sys.argv[1], sys.argv[2], sys.argv[3], set(sys.argv[4].split())
raw = sys.stdin.read().strip()
if not raw:
  print("ℹ️  Lista de devices vacía en el tenant.")
  raise SystemExit(0)

try:
  arr = json.loads(raw)
  if not isinstance(arr, list):
    print("ℹ️  /devices no devolvió una lista. No borro nada.")
    raise SystemExit(0)
except Exception:
  print("ℹ️  No se pudo parsear /devices. No borro nada.")
  raise SystemExit(0)

def delete(device_id: int):
  req = urllib.request.Request(
    f"{API}/devices/{device_id}",
    headers={"Authorization": f"Bearer {TOKEN}", "X-Tenant-ID": TENANT},
    method="DELETE",
  )
  try:
    with urllib.request.urlopen(req) as resp:
      # 204 esperado
      pass
    print(f"→ Borrado device {device_id}")
  except urllib.error.HTTPError as e:
    # Si ya no existe o alguna colisión, lo reportamos pero seguimos.
    print(f"⚠️  No se pudo borrar {device_id}: HTTP {e.code}")
  except Exception as e:
    print(f"⚠️  Error al borrar {device_id}: {e}")

for d in arr:
  did = d.get("id")
  if not isinstance(did, int):
    continue
  if str(did) not in KEEP:
    delete(did)
PY

# 5) Estado final
FINAL="$(curl -s -H "Authorization: Bearer $TOKEN" -H "X-Tenant-ID: $TENANT" "$API/devices" || true)"
if [ -n "$FINAL" ]; then
  echo "✅ Limpieza completa. Estado final:"
  echo "$FINAL" | python3 -m json.tool || echo "$FINAL"
else
  echo "✅ Limpieza completa. (/devices vacío)"
fi
