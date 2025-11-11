"""Code Execution Agent

Integrates MCP code execution runtime with Ada Maritime AI orchestrator.
Enables efficient tool usage via agent-generated code.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add mcp-code-execution to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mcp-code-execution"))

from runtime import CodeExecutionRuntime, ExecutionResult
from anthropic import Anthropic

from backend.config import get_config
from backend.logger import get_logger


logger = get_logger(__name__)


class CodeExecutionAgent:
    """
    Agent that uses code execution for efficient MCP tool usage.

    Instead of calling tools directly, the agent generates Python code
    that interacts with MCP servers, processes data locally, and returns
    only summary results.

    Benefits:
    - 98%+ token reduction on large data operations
    - Privacy-preserving intermediate results
    - State persistence across requests
    - Progressive tool loading
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Initialize runtime
        self.runtime = CodeExecutionRuntime()

        # Initialize Anthropic client
        app_config = get_config()
        self.client = Anthropic(api_key=app_config.api.anthropic_api_key)

        self.model = "claude-sonnet-4-20250514"

        logger.info("Code execution agent initialized")

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task using code execution approach.

        Args:
            task: Task definition with:
                - query: User query/request
                - context: Optional additional context
                - max_iterations: Max code generation iterations

        Returns:
            Task result with execution details
        """
        query = task.get("query", "")
        context = task.get("context", {})
        max_iterations = task.get("max_iterations", 3)

        logger.info(f"Executing task: {query[:100]}")

        # Generate system prompt
        system_prompt = self._build_system_prompt()

        # Conversation history
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        iterations = 0
        final_result = None

        while iterations < max_iterations:
            iterations += 1

            # Get code from Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=messages
            )

            # Extract code from response
            code = self._extract_code(response.content[0].text)

            if not code:
                # No code to execute, return text response
                final_result = {
                    "success": True,
                    "type": "text",
                    "content": response.content[0].text,
                    "iterations": iterations
                }
                break

            logger.info(f"Executing generated code (iteration {iterations})")

            # Execute code
            exec_result = self.runtime.execute(
                code,
                context=context,
                validate=True,
                preserve_privacy=True
            )

            if not exec_result.success:
                # Execution failed, provide error feedback
                messages.append({
                    "role": "assistant",
                    "content": response.content[0].text
                })
                messages.append({
                    "role": "user",
                    "content": f"Execution failed:\n{exec_result.stderr}\n\nPlease fix the code."
                })
                continue

            # Success - check if we have final result
            if exec_result.result is not None:
                final_result = {
                    "success": True,
                    "type": "code_execution",
                    "result": exec_result.result,
                    "stdout": exec_result.stdout,
                    "tools_used": exec_result.tools_used,
                    "tokens_saved": exec_result.tokens_saved,
                    "execution_time": exec_result.execution_time,
                    "iterations": iterations
                }
                break

            # No explicit result, use stdout
            messages.append({
                "role": "assistant",
                "content": response.content[0].text
            })
            messages.append({
                "role": "user",
                "content": f"Execution output:\n{exec_result.stdout}\n\nProvide final answer."
            })

        if not final_result:
            final_result = {
                "success": False,
                "error": "Max iterations reached without result"
            }

        # Add metrics
        final_result["total_tokens_saved"] = self.runtime.get_total_tokens_saved()

        logger.info(f"Task completed: {final_result.get('success')}, "
                   f"tokens saved: {final_result.get('tokens_saved', 0)}")

        return final_result

    def _build_system_prompt(self) -> str:
        """Build system prompt for code generation"""

        return """You are a maritime AI assistant with code execution capabilities.

Instead of calling tools directly, you write Python code that:
1. Searches for and loads MCP tools on-demand
2. Processes data locally (not through model context)
3. Returns only summary results

Available functions in execution context:
- search_tools(query, server=None, category=None) -> List[dict]
- load_tool(server, tool_name) -> callable
- list_servers() -> List[str]
- list_tools(server) -> List[dict]
- save_state(key, value) -> None
- load_state(key, default=None) -> Any

Example:
```python
# Find vessel tracking tools
tools = search_tools("vessel tracking")

# Load the tool
track = load_tool("maritime-data", "vessel_tracking")

# Get data
vessels = track(region="Mediterranean")

# Process locally (this is key! filter before returning)
large_vessels = [v for v in vessels if v['length'] > 100]

# Return summary only
result = {
    "total": len(vessels),
    "large": len(large_vessels),
    "summary": large_vessels[:5]  # Only top 5
}
```

Guidelines:
- Always filter/process data locally before returning
- Use search_tools() to find tools progressively
- Store intermediate state with save_state() for multi-step tasks
- Return concise summaries, not raw data dumps
- Assign final result to 'result' variable

Available MCP servers:
- maritime-data: vessel tracking, port info, AIS data
- weather: marine forecasts, conditions
- berth-management: marina berth availability, reservations

Write Python code to complete the user's request efficiently.
"""

    def _extract_code(self, text: str) -> Optional[str]:
        """Extract Python code from response"""
        # Look for code blocks
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                code = text[start:end].strip()
                # Check if it looks like Python
                if any(keyword in code for keyword in ["def ", "import ", "=", "for ", "if "]):
                    return code

        return None

    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics for current session"""
        history = self.runtime.get_execution_history()

        return {
            "total_executions": len(history),
            "successful": sum(1 for r in history if r.success),
            "failed": sum(1 for r in history if not r.success),
            "total_tokens_saved": self.runtime.get_total_tokens_saved(),
            "average_execution_time": (
                sum(r.execution_time for r in history) / len(history)
                if history else 0
            ),
            "tools_used": list(set(
                tool for r in history for tool in r.tools_used
            ))
        }
