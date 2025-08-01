#!/bin/bash

BASE_URL="http://localhost:5000"

echo "=== Blockchain API Examples ==="
echo

echo "1. Get API documentation:"
curl -s $BASE_URL/ | python -m json.tool
echo

echo "2. Create new user:"
curl -s -X POST $BASE_URL/users \
  -H "Content-Type: application/json" \
  -d '{"username": "charlie"}' | python -m json.tool
echo

echo "3. Check user balance:"
curl -s $BASE_URL/balance/alice | python -m json.tool
echo

echo "4. Create transaction:"
curl -s -X POST $BASE_URL/transaction \
  -H "Content-Type: application/json" \
  -d '{"sender": "alice", "receiver": "charlie", "amount": 5}' | python -m json.tool
echo

echo "5. View pending transactions:"
curl -s $BASE_URL/pending | python -m json.tool
echo

echo "6. Mine a block:"
curl -s -X POST $BASE_URL/mine | python -m json.tool
echo

echo "7. Get blockchain stats:"
curl -s $BASE_URL/blockchain/stats | python -m json.tool
echo

echo "8. Validate blockchain:"
curl -s -X POST $BASE_URL/validate | python -m json.tool