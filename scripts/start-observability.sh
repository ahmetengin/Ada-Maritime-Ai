#!/bin/bash
#
# Start Ada Maritime AI Observability System
# This script starts both the server and client for real-time monitoring
#

set -e

echo "🚀 Starting Ada Maritime AI Observability System..."
echo ""

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo "❌ Error: Bun is not installed"
    echo "Please install Bun: curl -fsSL https://bun.sh/install | bash"
    exit 1
fi

# Check if uv is installed (for hooks)
if ! command -v uv &> /dev/null; then
    echo "⚠️  Warning: uv is not installed (required for hooks)"
    echo "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# Install server dependencies
echo "📦 Installing server dependencies..."
cd apps/server
bun install
cd ../..

# Install client dependencies
echo "📦 Installing client dependencies..."
cd apps/client
bun install
cd ../..

# Start server in background
echo ""
echo "🌐 Starting observability server..."
cd apps/server
bun run dev &
SERVER_PID=$!
cd ../..

# Wait for server to start
sleep 3

# Start client
echo "🎨 Starting observability client..."
cd apps/client
bun run dev &
CLIENT_PID=$!
cd ../..

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Ada Maritime AI Observability System Running                ║"
echo "╟───────────────────────────────────────────────────────────────╢"
echo "║  Server:     http://localhost:4000                            ║"
echo "║  Dashboard:  http://localhost:5173                            ║"
echo "║                                                                ║"
echo "║  Press Ctrl+C to stop                                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Trap Ctrl+C and cleanup
trap "echo ''; echo '🛑 Stopping observability system...'; kill $SERVER_PID $CLIENT_PID 2>/dev/null; exit 0" INT TERM

# Wait for processes
wait
