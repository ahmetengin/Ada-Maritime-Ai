# MCP Code Execution for Ada Maritime AI

Efficient MCP tool usage via code execution, based on [Anthropic's code execution pattern](https://www.anthropic.com/engineering/code-execution-with-mcp).

## Overview

Instead of loading all MCP tool definitions into context and passing intermediate results through the model repeatedly, agents write Python code that:

1. **Loads tools on-demand** (progressive disclosure)
2. **Processes data locally** (in execution environment)
3. **Returns only summaries** to the model

### Token Savings Example

**Traditional Approach:**
```
Load all tools → 5,000 tokens
Get vessel data → 50,000 tokens
Filter in model → 50,000 tokens
Total: 105,000 tokens
```

**Code Execution Approach:**
```
Search & load 1 tool → 500 tokens
Execute & filter locally → (no model tokens)
Return summary → 500 tokens
Total: 1,000 tokens
Savings: 99% ✨
```

## Architecture

```
mcp-code-execution/
├── runtime.py          # Main execution runtime
├── tool_loader.py      # Progressive tool discovery
├── sandbox.py          # Secure code execution
├── privacy.py          # PII protection
├── servers/            # MCP servers as filesystem
│   ├── maritime-data/
│   │   ├── metadata.json
│   │   ├── vessel_tracking.py
│   │   └── port_info.py
│   ├── weather/
│   │   └── marine_forecast.py
│   └── berth-management/
│       └── check_availability.py
├── state/             # Session persistence
└── examples.py        # Usage examples
```

## Quick Start

### 1. Basic Usage

```python
from runtime import CodeExecutionRuntime

runtime = CodeExecutionRuntime()

code = """
# Search for tools
tools = search_tools("vessel tracking")

# Load tool on-demand
track = load_tool("maritime-data", "vessel_tracking")

# Get and filter data locally
vessels = track(region="Mediterranean")
large_vessels = [v for v in vessels if v['length'] > 100]

# Return summary only
result = {
    "total": len(vessels),
    "large": len(large_vessels),
    "summary": large_vessels[:5]
}
"""

result = runtime.execute(code)
print(f"Tokens saved: {result.tokens_saved}")
```

### 2. Integration with Ada Maritime AI

```python
from backend.orchestrator.code_execution_agent import CodeExecutionAgent

agent = CodeExecutionAgent()

result = agent.execute_task({
    "query": "Find available berths for an 18m yacht in Istanbul marinas",
    "context": {"user_id": "123"}
})

print(result)
```

### 3. Run Examples

```bash
cd mcp-code-execution
python examples.py
```

## Key Features

### 1. Progressive Tool Loading

Tools organized as filesystem - load only what you need:

```python
# Traditional: Load ALL tool definitions
# Code execution: Search and load on-demand

tools = search_tools("vessel tracking")  # Find relevant tools
track = load_tool("maritime-data", "vessel_tracking")  # Load only this one
```

### 2. Local Data Processing

Process large datasets without sending through model context:

```python
# Get 10,000 vessel records
vessels = track_vessels(region="Global")

# Filter locally (not through model!)
result = [v for v in vessels if v['length'] > 100 and v['speed'] < 5]

# Return only summary (100 tokens vs. 50,000 tokens)
```

### 3. Privacy Preservation

PII stays in execution environment by default:

```python
from privacy import PrivacyLayer

privacy = PrivacyLayer()

# Tokenize PII
text = "Contact john@example.com at IMO9876543"
tokenized, tokens = privacy.tokenize_pii(text)
# "Contact token_abc123@example.com at IMO7654321"

# Data flows between services without model exposure
```

### 4. State Persistence

Maintain state across operations:

```python
# Step 1: Search and save
favorites = find_vessels(...)
save_state("favorites", favorites)

# Step 2: Load and continue
favorites = load_state("favorites")
weather = check_weather_for_vessels(favorites)
```

### 5. Secure Sandboxing

Safe execution with resource limits:

```python
from sandbox import SecureSandbox, SandboxConfig

config = SandboxConfig(
    max_execution_time=30,  # seconds
    max_memory=512 * 1024 * 1024,  # 512MB
    allow_network=True,
    allowed_modules={'requests', 'pandas', 'json'}
)

sandbox = SecureSandbox(config)
result = sandbox.execute(code)
```

## MCP Servers

### Maritime Data Server

```python
# Vessel tracking
track = load_tool("maritime-data", "vessel_tracking")
vessels = track(
    region="Mediterranean",
    vessel_type="cargo",
    min_length=100
)

# Port information
ports = load_tool("maritime-data", "port_info")
marinas = ports(country="Turkey", has_fuel=True)
```

### Weather Server

```python
# Marine forecast
forecast = load_tool("weather", "marine_forecast")
weather = forecast(
    latitude=40.9823,
    longitude=29.0456,
    days=5,
    include_wind=True,
    include_waves=True
)
```

### Berth Management Server

```python
# Check availability
check = load_tool("berth-management", "check_availability")
berths = check(
    marina_id="kalamis",
    vessel_length=18.5,
    start_date="2025-11-15",
    end_date="2025-11-20"
)
```

## Creating New MCP Servers

### 1. Register Server

```python
from tool_loader import ToolLoader

loader = ToolLoader()
server_dir = loader.register_server(
    server_name="navigation",
    category="maritime",
    description="Navigation and routing tools"
)
```

### 2. Create Tool File

Create `servers/navigation/route_planner.py`:

```python
"""
Route planning tool - Calculate optimal routes.
"""

def execute(start_lat, start_lon, end_lat, end_lon):
    """
    Calculate optimal route between two points.

    Args:
        start_lat: Starting latitude
        start_lon: Starting longitude
        end_lat: Ending latitude
        end_lon: Ending longitude

    Returns:
        Route information with waypoints
    """
    # Implementation here
    return {
        "distance": 150.5,
        "duration": "12h 30m",
        "waypoints": [...]
    }
```

### 3. Use Tool

```python
# Tool is automatically discovered
tools = search_tools("route planning")

# Load and use
planner = load_tool("navigation", "route_planner")
route = planner(40.9, 29.0, 41.0, 28.5)
```

## API Reference

### Runtime Functions

Available in code execution context:

- `search_tools(query, server=None, category=None)` - Search for tools
- `load_tool(server, tool_name)` - Load tool function
- `list_servers()` - List all MCP servers
- `list_tools(server)` - List tools in server
- `save_state(key, value)` - Persist state
- `load_state(key, default=None)` - Load state

### CodeExecutionRuntime

```python
runtime = CodeExecutionRuntime(
    servers_dir="./servers",
    state_dir="./state",
    sandbox_config=SandboxConfig()
)

result = runtime.execute(
    code="...",
    context={},
    validate=True,
    preserve_privacy=True
)

# Metrics
metrics = runtime.get_metrics()
total_saved = runtime.get_total_tokens_saved()
```

### ExecutionResult

```python
@dataclass
class ExecutionResult:
    success: bool
    result: Any
    stdout: str
    stderr: str
    tools_used: List[str]
    tokens_saved: int
    execution_time: float
```

## Security Considerations

### Sandboxing

- CPU/memory limits enforced
- Network access controllable
- Module imports restricted
- Execution timeout (default 30s)

### Validation

```python
from sandbox import SandboxValidator

is_safe, error = SandboxValidator.validate(code)
if not is_safe:
    print(f"Unsafe code: {error}")
```

### Privacy

- PII automatically detected and tokenized
- Sensitive fields filtered from logs
- Intermediate results stay in environment

## Performance Metrics

From `examples.py`:

| Example | Traditional Tokens | Code Exec Tokens | Savings |
|---------|-------------------|------------------|---------|
| Vessel tracking | ~60,000 | ~1,000 | 98.3% |
| Marina search | ~40,000 | ~800 | 98.0% |
| Weather analysis | ~80,000 | ~1,200 | 98.5% |

Average savings: **98.3%**

## Best Practices

### 1. Filter Locally

```python
# ✅ Good: Filter before returning
vessels = get_vessels()
result = [v for v in vessels if v['length'] > 100][:10]

# ❌ Bad: Return all data
result = get_vessels()  # Returns 10,000 records
```

### 2. Progressive Loading

```python
# ✅ Good: Load on-demand
tools = search_tools("vessel")
track = load_tool("maritime-data", "vessel_tracking")

# ❌ Bad: Load all tools
for server in list_servers():
    for tool in list_tools(server):
        load_tool(server, tool['name'])
```

### 3. Return Summaries

```python
# ✅ Good: Concise summary
result = {
    "total": len(data),
    "summary": data[:5],
    "statistics": calculate_stats(data)
}

# ❌ Bad: Full dataset
result = data  # 50,000 tokens
```

### 4. Use State for Multi-Step

```python
# Step 1
favorites = find_items()
save_state("favorites", favorites)

# Step 2 (later)
favorites = load_state("favorites")
process_favorites(favorites)
```

## Troubleshooting

### Code execution timeout

Increase timeout in config:

```python
config = SandboxConfig(max_execution_time=60)
runtime = CodeExecutionRuntime(sandbox_config=config)
```

### Module not allowed

Add to allowed modules:

```python
config = SandboxConfig()
config.allowed_modules.add('your_module')
```

### Tool not found

Check tool registration:

```python
loader = ToolLoader()
servers = loader.list_servers()
tools = loader.list_tools("server_name")
```

## Contributing

To add new MCP servers:

1. Create directory in `servers/`
2. Add `metadata.json`
3. Create tool files with `execute()` function
4. Tools are auto-discovered

## References

- [Anthropic: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Ada Maritime AI](../README.md)

## License

Part of Ada Maritime AI system.
