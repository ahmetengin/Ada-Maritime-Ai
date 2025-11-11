"""MCP Code Execution Module

Implements efficient MCP tool usage via code execution approach.
Based on Anthropic's code execution pattern for reduced token usage.
"""

from .runtime import CodeExecutionRuntime
from .tool_loader import ToolLoader
from .sandbox import SecureSandbox

__all__ = ["CodeExecutionRuntime", "ToolLoader", "SecureSandbox"]
