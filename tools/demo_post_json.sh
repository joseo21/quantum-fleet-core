#!/usr/bin/env bash
set -euo pipefail

API=${API:-http://localhost:8000}

echo "→ Creando/upsert conector demo-post (base_url=postman-echo.com)…"
RESP=$(curl -sS -X POST "$API/connectors" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"demo-post",
    "base_url":"https://postman-echo.com",
    "auth_type":"none"
  }')
echo "$RESP" | jq .
ID=$(echo "$RESP" | jq -r .id)
echo "   id=$ID"

echo "→ POST /post con body JSON"
RESP2=$(curl -sS -X POST "$API/connectors/$ID/call" \
  -H "Content-Type: application/json" \
  -d '{
    "method":"POST",
    "path":"post",
    "body":{"alpha":123,"beta":"hola"}
  }')
echo "$RESP2" | jq .

echo "→ OK: el campo .json debería reflejar el payload enviado"
echo "$RESP2" | jq '.json'
