# Ada Maritime AI

⚓ Setur Marina POC - AI-powered marina management system with multi-agent orchestration

## Features

- **Big-5 Personality Orchestrator**: AI agents with personality-driven decision making
- **Berth Management**: Intelligent marina berth allocation and optimization
- **Email Service**: Automated customer communications
- **Multi-Agent Observability**: Real-time monitoring and visualization of agent workflows
- **Database Integration**: Mock Setur Marina database with comprehensive data models

## Quick Start

### Main Application

```bash
# Start infrastructure
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run streamlit_app.py
```

### Multi-Agent Observability System

Monitor and visualize all Claude Code agent activities in real-time:

```bash
# Start observability dashboard
./scripts/start-observability.sh
```

Then access:
- **Dashboard**: http://localhost:5173
- **API Server**: http://localhost:4000

See [OBSERVABILITY.md](./OBSERVABILITY.md) for detailed documentation.

## Infrastructure

- **PostgreSQL**: Primary data storage
- **Redis**: Caching and session management
- **Qdrant**: Vector database for semantic search
- **Neo4j**: Graph database for relationship mapping
- **SQLite**: Observability event storage

## Project Structure

```
Ada-Maritime-Ai/
├── .claude/                    # Claude Code hooks and configuration
│   ├── hooks/                  # Observability hooks (Python)
│   └── settings.json          # Hook configuration
├── apps/
│   ├── server/                # Observability server (Bun/TypeScript)
│   └── client/                # Observability dashboard (Vue 3)
├── backend/
│   ├── agents/                # AI agent implementations
│   ├── database/              # Database models and interfaces
│   ├── orchestrator/          # Big-5 orchestrator
│   ├── services/              # Email and other services
│   └── skills/                # Agent skills and capabilities
├── big-3-integration/         # Big-3 framework integration
├── kalamis-pitch/            # Kalamış Marina pitch materials
└── scripts/                   # Utility scripts
```

## Development

### Testing Observability Hooks

```bash
# Test the observability system
./scripts/test-hooks.sh
```

### Agent Development

The Big-5 orchestrator manages multiple AI agents with distinct personalities:
- **Openness**: Creative problem-solving
- **Conscientiousness**: Detail-oriented execution
- **Extraversion**: Customer-facing interactions
- **Agreeableness**: Collaborative decision making
- **Neuroticism**: Risk assessment and monitoring

## Documentation

- [Observability System](./OBSERVABILITY.md) - Multi-agent monitoring and visualization
- [Infrastructure](./INFRASTRUCTURE.md) - Infrastructure setup and configuration
- [Kalamış Pitch](./kalamis-pitch/PITCH_DECK.md) - Pitch deck and demo scenario

## License

Ada Maritime AI © 2025
