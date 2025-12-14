# -*- coding: utf-8 -*-
"""Tools שכבתית — כרגע מקומית, קלה להחלפה ל-MCP tools."""

from __future__ import annotations
import json
import os
from typing import Any, Dict, Optional

def restart_service(service: Optional[str]) -> Dict[str, Any]:
    # TODO: החלפה לכלי MCP אמיתי
    return {"ok": True, "service": service or "unknown", "action": "restart_service"}

def notify(alert: Dict[str, Any], *, reason: str = "escalate", diagnostics: Optional[Dict[str, Any]] = None) -> None:
    payload = {"reason": reason, "alert": alert, "diagnostics": diagnostics}
    print("NOTIFY:", json.dumps(payload, ensure_ascii=False))

def save_diagnostics_jsonl(path: str, diagnostics: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(diagnostics, ensure_ascii=False) + "\n")
