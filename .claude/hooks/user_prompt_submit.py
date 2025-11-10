#!/usr/bin/env python3
"""
User prompt submit hook for Ada Maritime AI observability.
Logs user prompts and interactions.
"""

import sys
import json
from send_event import send_event


def main():
    try:
        # Read prompt from stdin
        prompt_data = json.loads(sys.stdin.read())

        user_prompt = prompt_data.get("prompt", "")

        # Send event to observability server
        send_event(
            event_type="UserPromptSubmit",
            data={
                "prompt": user_prompt[:500] + ("..." if len(user_prompt) > 500 else ""),
                "promptLength": len(user_prompt),
            },
            summarize=True,
        )

        print(f"✓ User prompt logged", file=sys.stderr)

    except Exception as e:
        print(f"⚠ User prompt hook error: {e}", file=sys.stderr)
        # Don't block on hook errors
        pass


if __name__ == "__main__":
    main()
