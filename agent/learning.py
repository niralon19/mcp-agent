from __future__ import annotations

from typing import Any, Dict, List


def summarize_incidents(incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """שלב ראשון ל'למידה': סיכום גס של מה נעשה."""
    actions = {}
    for inc in incidents:
        a = (inc.get("action") or "unknown")
        actions[a] = actions.get(a, 0) + 1
    return {"incidents": len(incidents), "actions": actions}
