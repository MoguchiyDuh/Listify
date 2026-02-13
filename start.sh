#!/bin/bash

# Start Listify backend and frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"
mkdir -p "$PID_DIR"

echo "Starting Listify..."

# Start backend
echo "Starting backend..."
cd "$SCRIPT_DIR/backend"
uv run python main.py > "$SCRIPT_DIR/backend.log" 2>&1 &
echo $! > "$PID_DIR/backend.pid"
echo "Backend started (PID: $(cat $PID_DIR/backend.pid))"

# Start frontend
echo "Starting frontend..."
cd "$SCRIPT_DIR/frontend"
npm run dev > "$SCRIPT_DIR/frontend.log" 2>&1 &
echo $! > "$PID_DIR/frontend.pid"
echo "Frontend started (PID: $(cat $PID_DIR/frontend.pid))"

echo ""
echo "Listify is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Logs:"
echo "  Backend:  $SCRIPT_DIR/backend.log"
echo "  Frontend: $SCRIPT_DIR/frontend.log"
echo ""
echo "To stop: ./stop.sh"
