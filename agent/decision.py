# -*- coding: utf-8 -*-
"""Decision עם LLM — דומה לגרסה הראשונה, רק עם hook ל-diagnostics.

משתמש ב-Responses API.
"""

from __future__ import annotations
import os
from typing import Any, Dict

from openai import OpenAI

client = OpenAI()

SYSTEM = """אתה מהנדס NOC/SRE.
החזר JSON בלבד בצורה:
{"action":"...","confidence":0-1,"notes":"short"}
פעולות מותרות:
- restart_service
- escalate
- ignore
אל תכתוב טקסט נוסף מעבר ל-JSON.
"""

def decide(alert: Dict[str, Any], context: str = "", diag=None) -> Dict[str, Any]:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if diag:
        diag.step("llm_decision_start", {"model": model})

    user = {"alert": alert, "context": context or ""}

    resp = client.responses.create(
        timeout=20,
        max_output_tokens=120,
        model=model,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"{user}"},
        ],
        temperature=0,
    )

    text = resp.output_text.strip()
    if diag:
        diag.step("llm_decision_raw", {"text": text[:500]})

    import json
    try:
        out = json.loads(text)
    except Exception:
        lower = text.lower()
        action = "escalate"
        if "restart" in lower:
            action = "restart_service"
        elif "ignore" in lower:
            action = "ignore"
        out = {"action": action, "confidence": 0.3, "notes": "fallback_parse"}

    if diag:
        diag.step("llm_decision_result", {"action": out.get("action"), "confidence": out.get("confidence")})

    return out
