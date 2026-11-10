#!/usr/bin/env bash
# Sentinel-X helper scripts

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "${1:-help}" in
  backend)
    echo "==> Starting backend"
    (cd "$ROOT_DIR/backend" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000)
    ;;
  dashboard)
    echo "==> Starting dashboard"
    (cd "$ROOT_DIR/dashboard" && npm run dev)
    ;;
  train)
    echo "==> Training edge AI model"
    python "$ROOT_DIR/edge/ai/train.py"
    ;;
  test-backend)
    echo "==> Running backend tests"
    (cd "$ROOT_DIR/backend" && python -m pytest tests -v)
    ;;
  *)
    echo "Usage: ./scripts/run.sh {backend|dashboard|train|test-backend|help}"
    ;;
esac
