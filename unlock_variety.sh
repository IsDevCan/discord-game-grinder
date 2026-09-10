#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="$DIR/variety.log"
PIDFILE="$DIR/variety.pid"

# Stop existing grinder first so socket is free
"$DIR/stop.sh" 2>/dev/null

echo "[*] Launching 100+ Game Variety Badge Unlocker in background..."
nohup python3 -u "$DIR/variety_unlocker.py" > "$LOGFILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PIDFILE"

sleep 1
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "[✓] Variety Unlocker is running! (PID: $NEW_PID)"
    echo "[*] It will cycle through 65 unique official games."
    echo "[*] Check live progress with: ./variety_status.sh"
    echo "[*] Once finished, it will automatically resume normal game grinding!"
else
    echo "[X] Failed to start. Check $LOGFILE."
    rm -f "$PIDFILE"
fi
