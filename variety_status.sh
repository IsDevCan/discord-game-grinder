#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/variety.pid"
LOGFILE="$DIR/variety.log"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    PID=$(cat "$PIDFILE")
    echo "=========================================="
    echo "🟢 VARIETY UNLOCKER: Active (PID: $PID)"
    echo "=========================================="
    if [ -f "$LOGFILE" ]; then
        tail -n 12 "$LOGFILE"
    fi
else
    echo "=========================================="
    echo "🏁 VARIETY UNLOCKER: Inactive / Finished"
    echo "=========================================="
    if [ -f "$LOGFILE" ]; then
        tail -n 8 "$LOGFILE"
    fi
fi
