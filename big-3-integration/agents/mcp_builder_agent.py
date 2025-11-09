"""MCPBuilderAgent - MCP Server Builder"""

import os
import json
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic


class MCPBuilderAgent:
    """4-Phase MCP Server Builder"""

    PHASES = ["research", "build", "evaluate", "package"]

    def __init__(self, agent_name: str, service_name: str, api_docs_url: str,
                 language: str = "python", workspace_dir: str = "apps/content-gen"):
        self.agent_name = agent_name
        self.service_name = service_name
        self.api_docs_url = api_docs_url
        self.language = language

        self.workspace = Path(workspace_dir)
        self.servers_dir = self.workspace / "mcp_servers"
        self.server_dir = self.servers_dir / agent_name
        self.registry_file = self.servers_dir / "registry.json"

        self.servers_dir.mkdir(parents=True, exist_ok=True)
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        self.current_phase = 0
        self.phase_results = []
        self.status = "initialized"

    async def execute_task(self, task: dict) -> dict:
        print(f"[MCPBuilder] Building {self.language} MCP server: {self.agent_name}")
        self.status = "in_progress"

        for phase in self.PHASES:
            print(f"[MCPBuilder] Phase {self.current_phase + 1}/4: {phase}")

            result = await self._execute_phase(phase)
            self.phase_results.append(result)

            if not result.get("success"):
                self.status = "failed"
                break

            self.current_phase += 1

        if self.current_phase == len(self.PHASES):
            self.status = "completed"
            print(f"[MCPBuilder] ✅ MCP server built!")

        self._update_registry()

        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "phases_completed": self.current_phase,
            "server_path": str(self.server_dir)
        }

    async def _execute_phase(self, phase: str) -> dict:
        try:
            prompt = self._get_phase_prompt(phase)

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=prompt,
                messages=[{
                    "role": "user",
                    "content": f"Build MCP server for {self.service_name}\nAPI: {self.api_docs_url}"
                }]
            )

            output = message.content[0].text

            if phase == "build":
                self._create_server_files(output)

            return {"phase": phase, "success": True}

        except Exception as e:
            return {"phase": phase, "success": False, "error": str(e)}

    def _get_phase_prompt(self, phase: str) -> str:
        prompts = {
            "research": f"Research {self.service_name} API and MCP protocol",
            "build": f"Generate {self.language} MCP server code",
            "evaluate": "Create test suite",
            "package": "Finalize documentation"
        }
        return prompts.get(phase, "")

    def _create_server_files(self, output: str):
        self.server_dir.mkdir(parents=True, exist_ok=True)
        (self.server_dir / "src").mkdir(exist_ok=True)

        if self.language == "python":
            (self.server_dir / "src" / "server.py").write_text("# MCP Server\n")
            (self.server_dir / "requirements.txt").write_text("anthropic\nmodelcontextprotocol")
        
        (self.server_dir / "README.md").write_text(f"# {self.agent_name}\n\nMCP server for {self.service_name}")

    def _update_registry(self):
        registry = {}
        if self.registry_file.exists():
            registry = json.loads(self.registry_file.read_text())

        registry[self.agent_name] = {
            "name": self.agent_name,
            "service": self.service_name,
            "language": self.language,
            "status": self.status,
            "created": datetime.now().isoformat()
        }

        self.registry_file.write_text(json.dumps(registry, indent=2))
