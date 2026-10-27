#!/bin/sh
# Startup hook: launch a detached poller so the dock stays fresh.
# Startup commands are one-shot, so the loop lives in a background process.

MODULE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$MODULE_DIR/.poll.pid"
LOG_FILE="$MODULE_DIR/.poll.log"

interval="${LUVUS_SETTING_INTERVAL:-5}"
case "$interval" in
  ''|*[!0-9]*) interval=5 ;;
esac

# Kill a previous poller from an earlier startup (module re-link, re-enable).
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  kill "$(cat "$PID_FILE")" 2>/dev/null
  sleep 0.2
fi

nohup sh -c '
  while true; do
    LUVUS_BIN_PATH="${LUVUS_BIN_PATH:-luvus}" python3 "'"$MODULE_DIR"'/scripts/scan.py" >>"'"$LOG_FILE"'" 2>&1
    sleep '"$interval"'
  done
' >/dev/null 2>&1 &

echo $! > "$PID_FILE"
exit 0
