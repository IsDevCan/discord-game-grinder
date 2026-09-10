#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/grinder.pid"

if [ ! -f "$PIDFILE" ]; then
    echo "[!] No active grinder found."
    exit 0
fi

PID=$(cat "$PIDFILE")
if kill -0 "$PID" 2>/dev/null; then
    echo "[*] Stopping grinder (PID $PID)..."
    kill -TERM "$PID" 2>/dev/null
    sleep 1
    if kill -0 "$PID" 2>/dev/null; then
        kill -9 "$PID" 2>/dev/null
    fi
    echo "[✓] Grinder stopped."
else
    echo "[*] Grinder process was not running."
fi
rm -f "$PIDFILE"
