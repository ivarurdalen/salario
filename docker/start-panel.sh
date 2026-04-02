#!/usr/bin/env sh
set -eu

PORT="${PANEL_PORT:-5006}"
ADDRESS="${PANEL_ADDRESS:-0.0.0.0}"
ALLOW_WS_ORIGIN="${PANEL_ALLOW_WS_ORIGIN:-localhost:5006 127.0.0.1:5006}"

set -- python -m panel serve src/salario/app.py \
  --address "${ADDRESS}" \
  --port "${PORT}" \
  --session-history 0

for origin in ${ALLOW_WS_ORIGIN}; do
  set -- "$@" --allow-websocket-origin "${origin}"
done

exec "$@"
