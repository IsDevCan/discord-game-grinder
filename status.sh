#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/grinder.pid"
LOGFILE="$DIR/grinder.log"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    PID=$(cat "$PIDFILE")
    echo "=========================================="
    echo "🟢 STATUS: Active (PID: $PID)"
    echo "=========================================="
    if [ -f "$LOGFILE" ]; then
        tail -n 8 "$LOGFILE"
    fi
    echo ""
    echo "To stop: ./stop.sh"
else
    echo "=========================================="
    echo "🔴 STATUS: Inactive"
    echo "=========================================="
    echo "To start: ./start.sh valorant"
fi
