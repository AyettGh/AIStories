#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -x "$ROOT/server/venv/bin/python" ]]; then
  echo "Backend environment missing. Create it in server/venv and install requirements.txt."
  exit 1
fi

if [[ ! -d "$ROOT/client/node_modules" ]]; then
  echo "Frontend dependencies missing. Run npm install inside client/."
  exit 1
fi

trap 'kill 0' EXIT
(
  cd "$ROOT/server"
  ./venv/bin/python -m uvicorn api:app --reload --port 8000
) &
(
  cd "$ROOT/client"
  npm run dev
) &
wait
