#!/usr/bin/env bash
# Script idempotente: asegura token, device, dashboard y panel; luego imprime el dashboard completo.

API="http://localhost:8000"

# 0) Health + TOKEN
curl -sf "$API/health" >/dev/null || { echo "❌ API no disponible en $API"; exit 1; }
TOKEN=$(curl -s -X POST "$API/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=admin@example.com&password=Admin123!" \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("access_token",""))' )
[ -n "$TOKEN" ] || { echo "❌ No pude obtener TOKEN"; exit 1; }
echo "✅ TOKEN: ${TOKEN:0:24}..."

# 1) Asegurar un device en tenant 1
DEVICE_ID=$(curl -s -H "Authorization: Bearer $TOKEN" "$API/devices" \
 | python3 -c 'import sys,json
try:
  data=json.load(sys.stdin)
  print(data[0]["id"] if data else "")
except Exception:
  print("")')
if [ -z "$DEVICE_ID" ]; then
  DEVICE_ID=$(curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d '{"name":"Tracker demo","external_id":"dev-demo-001","tenant_id":1}' \
    "$API/devices" \
    | python3 -c 'import sys,json
try:
  print(json.load(sys.stdin)["id"])
except Exception:
  print("")')
fi
[ -n "$DEVICE_ID" ] || { echo "❌ No hay device y no se pudo crear"; exit 1; }
echo "✅ DEVICE_ID=$DEVICE_ID"

# 2) Crear/obtener dashboard "Operación Planta"
DASH_JSON=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Operación Planta","description":"KPIs tiempo real","is_public":false}' \
  "$API/tenants/1/dashboards")
DID=$(echo "$DASH_JSON" | python3 -c 'import sys,json
try:
  print(json.load(sys.stdin)["id"])
except Exception:
  print("")')
if [ -z "$DID" ]; then
  DID=$(curl -s -H "Authorization: Bearer $TOKEN" "$API/tenants/1/dashboards" \
    | python3 -c 'import sys,json
try:
  items=json.load(sys.stdin)
  print(next((d["id"] for d in items if d.get("name")=="Operación Planta"), ""))
except Exception:
  print("")')
fi
[ -n "$DID" ] || { echo "❌ No pude obtener/crear el dashboard"; exit 1; }
echo "✅ Dashboard ID=$DID"

# 3) Crear panel timeseries (usa el DEVICE_ID asegurado)
PANEL_JSON=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"title\":\"Temperatura promedio\",\"type\":\"timeseries\",\"config\":{\"device_id\":${DEVICE_ID},\"metric\":\"temp\",\"agg\":\"avg\",\"interval\":\"5m\",\"limit\":100},\"x\":0,\"y\":0,\"w\":8,\"h\":4}" \
  "$API/tenants/1/dashboards/${DID}/panels")
echo "→ Panel creado/respuesta:"
echo "$PANEL_JSON" | python3 -c 'import sys,json
try:
  print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))
except Exception:
  print("{}")'

# 4) Dashboard completo
echo "→ Dashboard completo:"
curl -s -H "Authorization: Bearer $TOKEN" "$API/tenants/1/dashboards/${DID}" \
 | python3 -c 'import sys,json
try:
  print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))
except Exception:
  print("{}")'

echo "✅ Listo."
