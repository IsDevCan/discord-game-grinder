#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/grinder.pid"
LOGFILE="$DIR/grinder.log"
MODE="${1:-auto}"

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[!] Grinder is already running (PID $PID)."
        echo "[*] Run ./status.sh to check progress, or ./stop.sh to stop."
        exit 0
    fi
fi

echo "[*] Starting Discord Game Grinder (Mode: $MODE)..."
nohup python3 -u "$DIR/grinder.py" --game "$MODE" > "$LOGFILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PIDFILE"

sleep 1
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "[✓] Grinder started successfully in background! (PID: $NEW_PID)"
    echo "[*] Mode: $MODE (Dynamic match scores & game rotation)"
    echo "[*] Logging to: $LOGFILE"
    echo "[*] Check status anytime with: ./status.sh"
    echo "[*] Stop anytime with: ./stop.sh"
else
    echo "[X] Failed to start. Check $LOGFILE for details."
    rm -f "$PIDFILE"
fi
