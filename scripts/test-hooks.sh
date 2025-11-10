#!/bin/bash
#
# Test Ada Maritime AI Observability Hooks
# Sends test events to verify the observability system
#

set -e

echo "🧪 Testing Ada Maritime AI Observability Hooks..."
echo ""

# Check if server is running
if ! curl -s http://localhost:4000/health > /dev/null; then
    echo "❌ Error: Observability server is not running"
    echo "Please start it with: ./scripts/start-observability.sh"
    exit 1
fi

echo "✓ Server is running"
echo ""

# Test sending events
echo "📤 Sending test events..."

# Test 1: User Prompt Submit
echo "1. Testing UserPromptSubmit event..."
uv run .claude/hooks/send_event.py \
    --event-type "UserPromptSubmit" \
    --data '{"prompt": "Test user prompt", "promptLength": 16}' \
    --summarize

sleep 1

# Test 2: Pre Tool Use
echo "2. Testing PreToolUse event..."
uv run .claude/hooks/send_event.py \
    --event-type "PreToolUse" \
    --data '{"toolName": "Bash", "toolInput": {"command": "echo test"}, "validated": true}' \
    --summarize

sleep 1

# Test 3: Post Tool Use
echo "3. Testing PostToolUse event..."
uv run .claude/hooks/send_event.py \
    --event-type "PostToolUse" \
    --data '{"toolName": "Bash", "success": true, "result": "test output"}' \
    --summarize

sleep 1

# Test 4: Subagent Start
echo "4. Testing SubagentStart event..."
uv run .claude/hooks/send_event.py \
    --event-type "SubagentStart" \
    --data '{"subagentType": "Explore", "description": "Test exploration"}' \
    --summarize

sleep 1

# Test 5: Subagent End
echo "5. Testing SubagentEnd event..."
uv run .claude/hooks/send_event.py \
    --event-type "SubagentEnd" \
    --data '{"subagentType": "Explore", "result": "Exploration complete"}' \
    --summarize

echo ""
echo "✅ All test events sent successfully!"
echo "Check the dashboard at http://localhost:5173 to see the events"
