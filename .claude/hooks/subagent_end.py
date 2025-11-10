#!/usr/bin/env python3
"""
Subagent end hook for Ada Maritime AI observability.
Tracks when subagents complete.
"""

import sys
import json
from send_event import send_event


def main():
    try:
        # Read subagent data from stdin
        subagent_data = json.loads(sys.stdin.read())

        subagent_type = subagent_data.get("subagent_type", "unknown")
        result = subagent_data.get("result", "")

        # Send event to observability server
        send_event(
            event_type="SubagentEnd",
            data={
                "subagentType": subagent_type,
                "result": result[:500] + ("..." if len(result) > 500 else ""),
            },
            summarize=True,
        )

        print(f"✓ Subagent end logged: {subagent_type}", file=sys.stderr)

    except Exception as e:
        print(f"⚠ Subagent end hook error: {e}", file=sys.stderr)
        # Don't block on hook errors
        pass


if __name__ == "__main__":
    main()
