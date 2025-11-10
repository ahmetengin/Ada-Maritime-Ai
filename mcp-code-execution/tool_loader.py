"""Tool Loader - Progressive MCP Tool Discovery

Implements filesystem-based tool organization for on-demand loading.
Reduces token usage by loading only necessary tool definitions.
"""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ToolMetadata:
    """Tool metadata for progressive loading"""
    name: str
    server: str
    description: str
    parameters: Dict[str, Any]
    file_path: str
    category: str = "general"

    def to_dict(self) -> dict:
        return asdict(self)


class ToolLoader:
    """
    Progressive tool loader for MCP servers.

    Organizes tools as filesystem:
    ./servers/
        maritime-data/
            vessel_tracking.py
            port_info.py
        weather/
            forecast.py
            marine_conditions.py
    """

    def __init__(self, servers_dir: str = "./mcp-code-execution/servers"):
        self.servers_dir = Path(servers_dir)
        self.servers_dir.mkdir(parents=True, exist_ok=True)

        self._tool_cache: Dict[str, ToolMetadata] = {}
        self._loaded_servers: set = set()

    def search_tools(
        self,
        query: str,
        server: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[ToolMetadata]:
        """
        Search for tools matching query.

        Progressive disclosure - load only matching tool definitions.

        Args:
            query: Search query (tool name or description keywords)
            server: Filter by server name
            category: Filter by category (maritime, weather, etc.)
            limit: Max results to return

        Returns:
            List of matching tool metadata
        """
        self._scan_servers()

        results = []
        query_lower = query.lower()

        for tool_meta in self._tool_cache.values():
            # Apply filters
            if server and tool_meta.server != server:
                continue
            if category and tool_meta.category != category:
                continue

            # Search in name and description
            if (query_lower in tool_meta.name.lower() or
                query_lower in tool_meta.description.lower()):
                results.append(tool_meta)

            if len(results) >= limit:
                break

        return results

    def get_tool(self, server: str, tool_name: str) -> Optional[ToolMetadata]:
        """Get specific tool metadata"""
        key = f"{server}/{tool_name}"
        return self._tool_cache.get(key)

    def list_servers(self) -> List[str]:
        """List all available MCP servers"""
        if not self.servers_dir.exists():
            return []
        return [d.name for d in self.servers_dir.iterdir() if d.is_dir()]

    def list_tools(self, server: str) -> List[ToolMetadata]:
        """List all tools in a server"""
        return [
            tool for tool in self._tool_cache.values()
            if tool.server == server
        ]

    def load_tool_function(self, server: str, tool_name: str) -> Optional[callable]:
        """
        Dynamically load tool function from file.

        This enables on-demand loading of tool implementations.
        """
        tool_meta = self.get_tool(server, tool_name)
        if not tool_meta:
            return None

        try:
            spec = importlib.util.spec_from_file_location(
                f"{server}.{tool_name}",
                tool_meta.file_path
            )
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for execute function
            if hasattr(module, 'execute'):
                return module.execute

            # Or function with tool name
            if hasattr(module, tool_name):
                return getattr(module, tool_name)

            return None

        except Exception as e:
            print(f"Error loading tool {server}/{tool_name}: {e}")
            return None

    def _scan_servers(self):
        """Scan servers directory and build tool cache"""
        if not self.servers_dir.exists():
            return

        for server_dir in self.servers_dir.iterdir():
            if not server_dir.is_dir():
                continue

            server_name = server_dir.name
            if server_name in self._loaded_servers:
                continue

            # Load server metadata
            meta_file = server_dir / "metadata.json"
            server_meta = {}
            if meta_file.exists():
                with open(meta_file) as f:
                    server_meta = json.load(f)

            # Scan tool files
            for tool_file in server_dir.glob("*.py"):
                if tool_file.name.startswith("_"):
                    continue

                tool_name = tool_file.stem
                tool_meta = self._extract_tool_metadata(
                    server_name,
                    tool_name,
                    tool_file,
                    server_meta
                )

                if tool_meta:
                    key = f"{server_name}/{tool_name}"
                    self._tool_cache[key] = tool_meta

            self._loaded_servers.add(server_name)

    def _extract_tool_metadata(
        self,
        server: str,
        tool_name: str,
        file_path: Path,
        server_meta: dict
    ) -> Optional[ToolMetadata]:
        """Extract tool metadata from Python file"""
        try:
            with open(file_path) as f:
                content = f.read()

            # Extract docstring for description
            description = "No description available"
            if '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end > start:
                    description = content[start:end].strip()

            # Extract parameters from function signature
            # Simplified - could use ast module for better parsing
            parameters = {}

            return ToolMetadata(
                name=tool_name,
                server=server,
                description=description,
                parameters=parameters,
                file_path=str(file_path),
                category=server_meta.get("category", "general")
            )

        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return None

    def register_server(
        self,
        server_name: str,
        category: str = "general",
        description: str = ""
    ):
        """Register a new MCP server"""
        server_dir = self.servers_dir / server_name
        server_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "name": server_name,
            "category": category,
            "description": description
        }

        meta_file = server_dir / "metadata.json"
        with open(meta_file, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create __init__.py
        init_file = server_dir / "__init__.py"
        init_file.write_text(f'"""MCP Server: {server_name}"""\n')

        return server_dir
