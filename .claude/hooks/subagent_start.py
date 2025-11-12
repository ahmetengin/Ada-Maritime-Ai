#!/usr/bin/env python3
"""
Subagent start hook for Ada Maritime AI observability.
Tracks when subagents are launched.
"""

import sys
import json
from send_event import send_event


def main():
    try:
        # Read subagent data from stdin
        subagent_data = json.loads(sys.stdin.read())

        subagent_type = subagent_data.get("subagent_type", "unknown")
        description = subagent_data.get("description", "")
        prompt = subagent_data.get("prompt", "")

        # Send event to observability server
        send_event(
            event_type="SubagentStart",
            data={
                "subagentType": subagent_type,
                "description": description,
                "prompt": prompt[:500] + ("..." if len(prompt) > 500 else ""),
            },
            summarize=True,
        )

        print(f"✓ Subagent start logged: {subagent_type}", file=sys.stderr)

    except Exception as e:
        print(f"⚠ Subagent start hook error: {e}", file=sys.stderr)
        # Don't block on hook errors
        pass


if __name__ == "__main__":
    main()
