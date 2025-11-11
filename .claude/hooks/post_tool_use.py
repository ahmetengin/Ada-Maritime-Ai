#!/usr/bin/env python3
"""
Post-tool use hook for Ada Maritime AI observability.
Captures tool execution results and outputs.
"""

import sys
import json
import os
from send_event import send_event


def summarize_output(output: str, max_length: int = 500) -> str:
    """Summarize long output for observability."""
    if len(output) <= max_length:
        return output

    return output[:max_length] + f"\n... (truncated {len(output) - max_length} chars)"


def main():
    try:
        # Read tool result from stdin
        tool_result = json.loads(sys.stdin.read())

        tool_name = tool_result.get("tool_name", "unknown")
        tool_input = tool_result.get("tool_input", {})
        result = tool_result.get("result", {})
        error = tool_result.get("error")

        # Summarize output if it's too long
        summarized_result = result
        if isinstance(result, str):
            summarized_result = summarize_output(result)
        elif isinstance(result, dict) and "output" in result:
            result_copy = result.copy()
            result_copy["output"] = summarize_output(str(result.get("output", "")))
            summarized_result = result_copy

        # Send event to observability server
        send_event(
            event_type="PostToolUse",
            data={
                "toolName": tool_name,
                "toolInput": tool_input,
                "result": summarized_result,
                "error": error,
                "success": error is None,
            },
            summarize=True,
        )

        print(f"✓ Tool execution logged: {tool_name}", file=sys.stderr)

    except Exception as e:
        print(f"⚠ Post-tool hook error: {e}", file=sys.stderr)
        # Don't block on hook errors
        pass


if __name__ == "__main__":
    main()
