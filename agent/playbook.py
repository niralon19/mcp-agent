# -*- coding: utf-8 -*-
"""Playbook רזה: Guardrail עדין לפעולות.

זה לא engine של צעדים. זה רק "מותר/אסור" לפי סוג התראה (לפי metric/alert_name).
אם אין התאמה — לא חוסמים (כדי לשמור על פשטות והתנהגות דומה לגרסה הראשונה).
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "cpu": {"allow_actions": ["restart_service"]},
    "memory": {"allow_actions": ["restart_service"]},
    "disk": {"allow_actions": []},
}

def _key_from_alert(alert: Dict[str, Any]) -> Optional[str]:
    return alert.get("metric") or alert.get("alert_name") or alert.get("name")

def is_action_allowed(alert: Dict[str, Any], action: str) -> bool:
    key = _key_from_alert(alert)
    if not key:
        return True
    pb = PLAYBOOKS.get(key)
    if not pb:
        return True
    allow: List[str] = pb.get("allow_actions", [])
    return action in allow
