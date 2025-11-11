"""Code Execution Runtime

Main runtime for executing agent-generated code with MCP tool access.
Implements the efficient code execution pattern from Anthropic's blog.
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict

try:
    from .tool_loader import ToolLoader, ToolMetadata
    from .sandbox import SecureSandbox, SandboxConfig, SandboxValidator
    from .privacy import PrivacyLayer
except ImportError:
    from tool_loader import ToolLoader, ToolMetadata
    from sandbox import SecureSandbox, SandboxConfig, SandboxValidator
    from privacy import PrivacyLayer


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    result: Any
    stdout: str
    stderr: str
    tools_used: List[str]
    tokens_saved: int  # Estimated tokens saved vs. traditional approach
    execution_time: float

    def to_dict(self) -> dict:
        return asdict(self)


class CodeExecutionRuntime:
    """
    Code execution runtime for efficient MCP tool usage.

    Key features:
    - Progressive tool loading (search_tools)
    - Local data processing
    - Privacy-preserving execution
    - State persistence
    - Token usage optimization

    Example:
        runtime = CodeExecutionRuntime()

        # Agent generates code like:
        code = '''
        # Search for vessel tracking tools
        tools = search_tools("vessel tracking")

        # Load and use the tool
        track_vessel = load_tool("maritime-data", "vessel_tracking")
        vessels = track_vessel(region="Mediterranean")

        # Filter locally (not through model context!)
        large_vessels = [v for v in vessels if v['length'] > 100]

        # Return only summary
        result = {
            "total": len(vessels),
            "large_vessels": len(large_vessels),
            "summary": large_vessels[:5]
        }
        '''

        result = runtime.execute(code)
    """

    def __init__(
        self,
        servers_dir: str = "./mcp-code-execution/servers",
        state_dir: str = "./mcp-code-execution/state",
        sandbox_config: Optional[SandboxConfig] = None
    ):
        self.tool_loader = ToolLoader(servers_dir)
        self.sandbox = SecureSandbox(sandbox_config or SandboxConfig())
        self.privacy = PrivacyLayer()

        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self._execution_history: List[ExecutionResult] = []
        self._session_state: Dict[str, Any] = {}

    def execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        validate: bool = True,
        preserve_privacy: bool = True
    ) -> ExecutionResult:
        """
        Execute agent-generated code with MCP tool access.

        Args:
            code: Python code to execute
            context: Additional context to inject
            validate: Validate code before execution
            preserve_privacy: Apply privacy protections

        Returns:
            ExecutionResult with outcome and metrics
        """
        import time
        start_time = time.time()

        # Validate code
        if validate:
            is_safe, error = SandboxValidator.validate(code)
            if not is_safe:
                return ExecutionResult(
                    success=False,
                    result=None,
                    stdout="",
                    stderr=f"Validation failed: {error}",
                    tools_used=[],
                    tokens_saved=0,
                    execution_time=0
                )

        # Prepare execution context with MCP tools
        exec_context = self._prepare_mcp_context(context or {})

        # Apply privacy layer if enabled
        if preserve_privacy:
            code = self.privacy.sanitize_code(code)

        # Execute in sandbox
        tools_used = []
        try:
            result, stdout, stderr = self.sandbox.execute(code, exec_context)

            # Track which tools were used
            if '_tools_used' in exec_context:
                tools_used = exec_context['_tools_used']

            # Calculate token savings
            tokens_saved = self._estimate_tokens_saved(code, result, tools_used)

            execution_time = time.time() - start_time

            exec_result = ExecutionResult(
                success=True,
                result=result,
                stdout=stdout,
                stderr=stderr,
                tools_used=tools_used,
                tokens_saved=tokens_saved,
                execution_time=execution_time
            )

            self._execution_history.append(exec_result)
            return exec_result

        except Exception as e:
            execution_time = time.time() - start_time

            return ExecutionResult(
                success=False,
                result=None,
                stdout="",
                stderr=str(e),
                tools_used=tools_used,
                tokens_saved=0,
                execution_time=execution_time
            )

    def _prepare_mcp_context(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare execution context with MCP tool functions"""

        tools_used = []

        def search_tools(
            query: str,
            server: Optional[str] = None,
            category: Optional[str] = None
        ) -> List[Dict[str, Any]]:
            """Search for available MCP tools"""
            results = self.tool_loader.search_tools(query, server, category)
            return [tool.to_dict() for tool in results]

        def load_tool(server: str, tool_name: str) -> callable:
            """Load an MCP tool function"""
            func = self.tool_loader.load_tool_function(server, tool_name)
            if not func:
                raise ValueError(f"Tool {server}/{tool_name} not found")

            tools_used.append(f"{server}/{tool_name}")

            # Wrap function to track usage
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapped

        def list_servers() -> List[str]:
            """List all available MCP servers"""
            return self.tool_loader.list_servers()

        def list_tools(server: str) -> List[Dict[str, Any]]:
            """List all tools in a server"""
            tools = self.tool_loader.list_tools(server)
            return [tool.to_dict() for tool in tools]

        def save_state(key: str, value: Any):
            """Persist state across executions"""
            self._session_state[key] = value

        def load_state(key: str, default: Any = None) -> Any:
            """Load persisted state"""
            return self._session_state.get(key, default)

        # MCP context
        mcp_context = {
            'search_tools': search_tools,
            'load_tool': load_tool,
            'list_servers': list_servers,
            'list_tools': list_tools,
            'save_state': save_state,
            'load_state': load_state,
            '_tools_used': tools_used,
            **user_context
        }

        return mcp_context

    def _estimate_tokens_saved(
        self,
        code: str,
        result: Any,
        tools_used: List[str]
    ) -> int:
        """
        Estimate tokens saved vs. traditional approach.

        Traditional: All tool definitions + intermediate results in context
        Code execution: Only final result returned to model
        """
        # Rough estimates (tokens ≈ characters / 4)

        # Saved from not loading all tool definitions
        total_tools = len(list(self.tool_loader._tool_cache.values()))
        tools_loaded = len(tools_used)
        avg_tool_def_size = 500  # chars
        saved_from_definitions = (total_tools - tools_loaded) * avg_tool_def_size / 4

        # Saved from local data processing
        # Assume intermediate data could be 10x larger than final result
        result_size = len(str(result)) if result else 0
        saved_from_processing = (result_size * 10) / 4

        return int(saved_from_definitions + saved_from_processing)

    def get_execution_history(self) -> List[ExecutionResult]:
        """Get execution history for current session"""
        return self._execution_history

    def get_total_tokens_saved(self) -> int:
        """Calculate total tokens saved in session"""
        return sum(r.tokens_saved for r in self._execution_history)

    def persist_state(self, filename: str = "session_state.json"):
        """Persist session state to disk"""
        state_file = self.state_dir / filename

        state_data = {
            'session_state': self._session_state,
            'execution_history': [r.to_dict() for r in self._execution_history]
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)

    def restore_state(self, filename: str = "session_state.json"):
        """Restore session state from disk"""
        state_file = self.state_dir / filename

        if not state_file.exists():
            return

        with open(state_file) as f:
            state_data = json.load(f)

        self._session_state = state_data.get('session_state', {})

        # Note: execution_history is not restored (results may not be serializable)
