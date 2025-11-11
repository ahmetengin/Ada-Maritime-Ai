# Ada Maritime AI - Multi-Agent Observability System

Real-time monitoring and visualization system for Claude Code multi-agent workflows in the Ada Maritime AI project.

## 🎯 Overview

This observability system provides comprehensive real-time tracking and visualization of all Claude Code agent activities, including:

- **User Prompts**: Track all user interactions and requests
- **Tool Usage**: Monitor pre/post execution of tools (Bash, Read, Write, etc.)
- **Subagent Activity**: Track spawned subagents (Explore, Plan, etc.)
- **Session Management**: Filter and view events by session
- **Live Dashboard**: Real-time WebSocket-powered visualization

## 🏗️ Architecture

```
┌─────────────────┐
│  Claude Code    │
│   + Hooks       │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────┐      WebSocket      ┌─────────────────┐
│  Observability  │◄────────────────────┤  Vue Dashboard  │
│     Server      │                     │   (Port 5173)   │
│  (Port 4000)    │                     └─────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │
│  (WAL Mode)     │
└─────────────────┘
```

### Components

1. **Hooks** (`.claude/hooks/`)
   - Python scripts triggered by Claude Code lifecycle events
   - Send events to observability server
   - Validate dangerous commands (safety checks)

2. **Server** (`apps/server/`)
   - Bun/TypeScript HTTP and WebSocket server
   - SQLite database with WAL mode for concurrent access
   - REST API for event retrieval and management

3. **Client** (`apps/client/`)
   - Vue 3 real-time dashboard
   - Canvas-based activity pulse visualization
   - Multi-criteria filtering (app, session, event type)

## 🚀 Quick Start

### Prerequisites

- [Bun](https://bun.sh/) - JavaScript runtime and package manager
- [Astral uv](https://github.com/astral-sh/uv) - Python package manager for hooks
- Claude Code CLI

### Installation

1. **Install Bun** (if not already installed):
```bash
curl -fsSL https://bun.sh/install | bash
```

2. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Start the observability system**:
```bash
./scripts/start-observability.sh
```

This will:
- Install all dependencies
- Start the server on `http://localhost:4000`
- Start the dashboard on `http://localhost:5173`

### Testing

Test the hooks system with sample events:

```bash
./scripts/test-hooks.sh
```

This will send test events to verify the system is working correctly.

## 📊 Dashboard Features

### Real-Time Event Timeline
- Live-updating event cards with color-coded event types
- Auto-scroll to latest events
- Expandable event data with syntax highlighting

### Activity Pulse Chart
- Canvas-based visualization showing agent activity intensity
- Real-time pulse animation
- 60-second rolling window

### Filtering System
- Filter by source application
- Filter by session ID
- Filter by event type
- Clear filters button

### Event Types

| Event Type | Description | Color |
|------------|-------------|-------|
| `UserPromptSubmit` | User sends a prompt to Claude | Green |
| `PreToolUse` | Before tool execution (with validation) | Orange |
| `PostToolUse` | After tool execution (with results) | Blue |
| `SubagentStart` | Subagent spawned | Purple |
| `SubagentEnd` | Subagent completed | Magenta |

## 🔧 Configuration

### Server Configuration

Environment variables for `apps/server/`:

```bash
PORT=4000                    # Server port (default: 4000)
DATABASE_PATH=./observability.db  # SQLite database path
```

### Client Configuration

Environment variables for `apps/client/` (create `.env` file):

```bash
VITE_API_URL=http://localhost:4000      # Server API URL
VITE_WS_URL=ws://localhost:4000/ws      # WebSocket URL
VITE_MAX_EVENTS_TO_DISPLAY=500          # Max events in UI
```

### Hooks Configuration

The hooks are configured in `.claude/settings.json`:

```json
{
  "preToolUseHook": "uv run .claude/hooks/pre_tool_use.py",
  "postToolUseHook": "uv run .claude/hooks/post_tool_use.py",
  "userPromptSubmitHook": "uv run .claude/hooks/user_prompt_submit.py",
  "subagentStartHook": "uv run .claude/hooks/subagent_start.py",
  "subagentEndHook": "uv run .claude/hooks/subagent_end.py"
}
```

## 🛡️ Safety Features

The `pre_tool_use.py` hook includes validation to block dangerous commands:

- `rm -rf /` - Recursive deletion of root
- `:(){ :|:& };:` - Fork bomb
- `dd if=/dev/zero` - Disk wiping
- `mkfs.*` - Filesystem formatting
- `chmod -R 777 /` - Dangerous permission changes

Events are logged but command execution is blocked when dangerous patterns are detected.

## 📡 API Reference

### REST Endpoints

#### POST `/events`
Create a new event

**Request Body:**
```json
{
  "eventType": "PostToolUse",
  "sourceApp": "ada-maritime-ai",
  "sessionId": "abc123...",
  "timestamp": "2025-11-10T12:00:00.000Z",
  "data": {
    "toolName": "Bash",
    "success": true
  }
}
```

#### GET `/events?limit=100&sourceApp=ada-maritime-ai`
Retrieve events with optional filters

**Query Parameters:**
- `limit` - Max events to return (default: 100)
- `sourceApp` - Filter by source application
- `sessionId` - Filter by session ID
- `eventType` - Filter by event type

#### GET `/sessions`
Get all unique session IDs

#### GET `/sources`
Get all unique source applications

#### GET `/health`
Health check endpoint

### WebSocket

Connect to `ws://localhost:4000/ws` to receive real-time events.

**Message Types:**

**Connected:**
```json
{
  "type": "connected",
  "message": "Connected to Ada Maritime AI Observability",
  "timestamp": "2025-11-10T12:00:00.000Z"
}
```

**Event:**
```json
{
  "type": "event",
  "event": {
    "id": 123,
    "eventType": "PostToolUse",
    "sourceApp": "ada-maritime-ai",
    "sessionId": "abc123...",
    "timestamp": "2025-11-10T12:00:00.000Z",
    "data": { ... }
  }
}
```

## 🔍 Troubleshooting

### Server won't start
- Check if port 4000 is already in use: `lsof -i :4000`
- Verify Bun is installed: `bun --version`
- Check server logs for errors

### Hooks not sending events
- Verify uv is installed: `uv --version`
- Check that `.claude/settings.json` is properly configured
- Run test hooks: `./scripts/test-hooks.sh`
- Check server logs to see if events are being received

### Dashboard not updating
- Verify WebSocket connection (check browser console)
- Ensure server is running on port 4000
- Clear browser cache and reload

### Database issues
- Delete `observability.db` to reset
- Check file permissions on database file
- Verify SQLite is available

## 🚦 Development

### Server Development

```bash
cd apps/server
bun install
bun run dev  # Watch mode with auto-reload
```

### Client Development

```bash
cd apps/client
bun install
bun run dev  # Vite dev server with HMR
```

### Building for Production

**Server:**
```bash
cd apps/server
bun run build
bun run dist/index.js
```

**Client:**
```bash
cd apps/client
bun run build
# Serve dist/ folder with your preferred static server
```

## 📝 Adding Custom Events

To send custom events from your code:

```bash
uv run .claude/hooks/send_event.py \
    --event-type "CustomEvent" \
    --data '{"key": "value", "message": "Custom event data"}' \
    --summarize
```

Or programmatically in Python:

```python
from send_event import send_event

send_event(
    event_type="CustomEvent",
    data={
        "key": "value",
        "message": "Custom event data"
    },
    summarize=True
)
```

## 🤝 Contributing

When adding new hooks or modifying the observability system:

1. Test hooks with `./scripts/test-hooks.sh`
2. Verify events appear in the dashboard
3. Check that dangerous commands are properly blocked
4. Update this documentation

## 📄 License

Part of the Ada Maritime AI project.

## 🙏 Credits

Inspired by [claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) by @disler.

---

**Ada Maritime AI** - Revolutionizing marina management with AI-powered automation 🚢⚓
