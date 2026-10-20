#!/usr/bin/env bash
# Usage: scripts/smoke_test.sh [base_url]   (fails with non-zero exit on any problem)
set -euo pipefail
URL="${1:-http://localhost:8000}"

for i in $(seq 1 30); do
  if curl -fsS "$URL/health" > /dev/null 2>&1; then break; fi
  sleep 2
  [ "$i" -eq 30 ] && { echo "API did not become healthy"; exit 1; }
done
echo "health: $(curl -fsS "$URL/health")"

RESP=$(curl -fsS -X POST "$URL/predict" -H "Content-Type: application/json" -d '{
  "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
  "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3,
  "ca": 0, "thal": 6}')
echo "predict: $RESP"
echo "$RESP" | grep -q '"confidence"' || { echo "unexpected response"; exit 1; }
echo "smoke test passed"
