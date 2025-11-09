# Big-3 Integration

Autonomous agent builders for skill creation and MCP server generation.

## Components

### 1. SkillCreatorAgent
6-phase autonomous skill creation:
- Research
- Design
- Implement
- Validate
- Package
- Document

### 2. MCPBuilderAgent
4-phase MCP server builder:
- Research API
- Build server code
- Evaluate & test
- Package for deployment

## Usage

```python
from big_3_integration.agents import SkillCreatorAgent, MCPBuilderAgent

# Create a new skill
skill_agent = SkillCreatorAgent(
    agent_name="yacht_maintenance",
    skill_type="maintenance",
    description="Track and schedule yacht maintenance tasks"
)
result = await skill_agent.execute_task({"operation": "create_skill"})

# Build MCP server
mcp_agent = MCPBuilderAgent(
    agent_name="weather_api",
    service_name="OpenWeatherMap",
    api_docs_url="https://openweathermap.org/api"
)
result = await mcp_agent.execute_task({})
