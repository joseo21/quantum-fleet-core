#!/usr/bin/env bash
set -euo pipefail

API=${API:-http://localhost:8000}

echo "→ Creando conector demo-header…"
RESP=$(curl -sS -X POST "$API/connectors" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"demo-header",
    "base_url":"https://postman-echo.com",
    "auth_type":"none",
    "headers": { "X-API-KEY": "X-API-KEY-123" }
  }')
ID_HEADER=$(echo "$RESP" | jq -r .id)
echo "   id=$ID_HEADER"

echo "→ GET /headers (header X-API-KEY)…"
curl -sS -X POST "$API/connectors/$ID_HEADER/call" \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","path":"headers"}' | jq '.headers."x-api-key"'

echo "→ Creando conector demo-query…"
RESP=$(curl -sS -X POST "$API/connectors" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"demo-query",
    "base_url":"https://postman-echo.com",
    "auth_type":"none",
    "params": { "apikey": "apikey-xyz" }
  }')
ID_QUERY=$(echo "$RESP" | jq -r .id)
echo "   id=$ID_QUERY"

echo "→ GET /get?q=ping (con apikey)…"
curl -sS -X POST "$API/connectors/$ID_QUERY/call" \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","path":"get","query":{"q":"ping"}}' | jq '.args'

echo "→ Creando conector demo-bearer…"
RESP=$(curl -sS -X POST "$API/connectors" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"demo-bearer",
    "base_url":"https://postman-echo.com",
    "auth_type":"bearer",
    "auth_token":"TU_TOKEN_SUPER_SECRETO"
  }')
ID_BEARER=$(echo "$RESP" | jq -r .id)
echo "   id=$ID_BEARER"

echo "→ GET /headers (ver Authorization: Bearer)…"
curl -sS -X POST "$API/connectors/$ID_BEARER/call" \
  -H "Content-Type: application/json" \
  -d '{"method":"GET","path":"headers"}' | jq '.headers.Authorization // .headers.authorization'

echo "→ Últimos logs:"
docker compose exec -T postgres sh -lc \
'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -A -F"|" -c "SELECT id,at,direction,status,method,path FROM connector_logs ORDER BY id DESC LIMIT 10;"'
