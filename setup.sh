#!/bin/bash

# Listify Auto Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================"
echo "  Listify Auto Setup"
echo "======================================"
echo ""

# Check Python version
echo "[1/6] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Install it first."
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python $PYTHON_VERSION found"

# Check Node version
echo ""
echo "[2/6] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Install Node.js >= 20.0.0"
    exit 1
fi
NODE_VERSION=$(node --version | sed 's/v//')
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
if [ "$NODE_MAJOR" -lt 20 ]; then
    echo "Error: Node.js version must be >= 20.0.0 (current: $NODE_VERSION)"
    exit 1
fi
echo "Node.js $NODE_VERSION found"

# Setup backend
echo ""
echo "[3/6] Setting up backend..."
cd "$SCRIPT_DIR/backend"

if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "Installing Python dependencies using uv..."
uv sync

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Warning: backend/.env not found!"
    echo "Copy .env.example or create .env manually"
fi

# Run migrations
echo "Running database migrations..."
uv run alembic upgrade head

echo "Backend setup complete"

# Setup frontend
echo ""
echo "[4/6] Setting up frontend..."
cd "$SCRIPT_DIR/frontend"

echo "Installing Node dependencies..."
npm install

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Warning: frontend/.env not found!"
    echo "Create .env with VITE_API_BASE_URL"
fi

echo "Frontend setup complete"

# Create necessary directories
echo ""
echo "[5/6] Creating directories..."
mkdir -p "$SCRIPT_DIR/backend/logs"
mkdir -p "$SCRIPT_DIR/.pids"
echo "Directories created"

# Make scripts executable
echo ""
echo "[6/6] Making scripts executable..."
chmod +x "$SCRIPT_DIR/start.sh" "$SCRIPT_DIR/stop.sh" 2>/dev/null || true

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Configure backend/.env (CORS, SECRET_KEY, API keys)"
echo "  2. Configure frontend/.env (VITE_API_BASE_URL)"
echo "  3. Run: ./start.sh"
echo ""
