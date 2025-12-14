from __future__ import annotations

from typing import Dict


def notify(channel: str, message: str) -> Dict[str, str]:
    """דמו: שליחת הודעה (Slack/Teams/Email)."""
    print(f"[NOTIFY:{channel}] {message}")
    return {"channel": channel, "result": "sent"}
