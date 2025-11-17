#!/bin/bash

# Stop Listify backend and frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"

echo "Stopping Listify..."

# Stop backend
if [ -f "$PID_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$PID_DIR/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID"
        rm "$PID_DIR/backend.pid"
        echo "Backend stopped"
    else
        echo "Backend not running"
        rm "$PID_DIR/backend.pid"
    fi
else
    echo "Backend PID file not found"
fi

# Stop frontend
if [ -f "$PID_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PID_DIR/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID"
        rm "$PID_DIR/frontend.pid"
        echo "Frontend stopped"
    else
        echo "Frontend not running"
        rm "$PID_DIR/frontend.pid"
    fi
else
    echo "Frontend PID file not found"
fi

echo "Listify stopped"
