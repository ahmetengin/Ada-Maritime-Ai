#!/usr/bin/env python3
"""
Pre-tool use hook for Ada Maritime AI observability.
Captures and validates tool usage before execution.
"""

import sys
import json
import os
from send_event import send_event


def validate_command(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """
    Validate command for safety.
    Returns (is_safe, message)
    """

    # Dangerous patterns to block
    dangerous_patterns = [
        "rm -rf /",
        ":(){ :|:& };:",  # Fork bomb
        "dd if=/dev/zero",
        "mkfs.",
        "chmod -R 777 /",
    ]

    if tool_name == "Bash":
        command = tool_input.get("command", "")

        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"🛑 Blocked dangerous command pattern: {pattern}"

    return True, "✓ Command validated"


def main():
    try:
        # Read tool information from stdin
        tool_data = json.loads(sys.stdin.read())

        tool_name = tool_data.get("tool_name", "unknown")
        tool_input = tool_data.get("tool_input", {})

        # Validate command
        is_safe, message = validate_command(tool_name, tool_input)

        # Send event to observability server
        send_event(
            event_type="PreToolUse",
            data={
                "toolName": tool_name,
                "toolInput": tool_input,
                "validated": is_safe,
                "validationMessage": message,
            },
            summarize=True,
        )

        # Block execution if unsafe
        if not is_safe:
            print(message, file=sys.stderr)
            sys.exit(1)

        # Allow execution
        print(message, file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        print(f"⚠ Pre-tool hook error: {e}", file=sys.stderr)
        # Don't block on hook errors
        sys.exit(0)


if __name__ == "__main__":
    main()
