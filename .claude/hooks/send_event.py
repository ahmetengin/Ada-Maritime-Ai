#!/usr/bin/env python3
"""
Universal event transmitter for Ada Maritime AI observability.
Sends events to the observability server for real-time monitoring.
"""

import sys
import json
import os
import argparse
from datetime import datetime
import requests
from typing import Optional


def send_event(
    event_type: str,
    source_app: str = "ada-maritime-ai",
    session_id: Optional[str] = None,
    data: Optional[dict] = None,
    summarize: bool = False,
) -> None:
    """Send event to observability server."""

    server_url = os.getenv("OBSERVABILITY_SERVER_URL", "http://localhost:4000")

    # Get session ID from environment if not provided
    if not session_id:
        session_id = os.getenv("CLAUDE_SESSION_ID", "default")

    # Prepare event payload
    event = {
        "eventType": event_type,
        "sourceApp": source_app,
        "sessionId": session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": data or {},
    }

    # Add summarization flag
    if summarize:
        event["data"]["summarized"] = True

    try:
        response = requests.post(
            f"{server_url}/events",
            json=event,
            timeout=5,
        )

        if response.status_code == 200:
            print(f"✓ Event sent: {event_type}", file=sys.stderr)
        else:
            print(f"⚠ Failed to send event: {response.status_code}", file=sys.stderr)

    except requests.exceptions.RequestException as e:
        # Silently fail - don't block Claude Code execution
        print(f"⚠ Observability server unreachable: {e}", file=sys.stderr)
    except Exception as e:
        print(f"⚠ Error sending event: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Send observability event")
    parser.add_argument("--event-type", required=True, help="Type of event")
    parser.add_argument("--source-app", default="ada-maritime-ai", help="Source application name")
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--data", help="Event data as JSON string")
    parser.add_argument("--summarize", action="store_true", help="Summarize event data")

    args = parser.parse_args()

    # Parse data if provided
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"⚠ Invalid JSON data: {args.data}", file=sys.stderr)
            data = {"raw": args.data}

    send_event(
        event_type=args.event_type,
        source_app=args.source_app,
        session_id=args.session_id,
        data=data,
        summarize=args.summarize,
    )


if __name__ == "__main__":
    main()
