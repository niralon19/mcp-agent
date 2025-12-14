from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .prompts import DECISION_PROMPT
from diagnostics.context import DiagnosticsContext


class DecisionError(RuntimeError):
    pass


def _fallback_decision(context: Dict[str, Any]) -> Dict[str, Any]:
    # fallback דטרמיניסטי: לפי service_health
    health = context.get("service_health", {}) or {}
    status = (health.get("status") or "").lower()
    env = (context.get("notes", {}) or {}).get("env", "unknown")

    if status == "down" and env != "prod":
        return {"action": "restart_service", "action_input": {"service": health.get("service")}, "reason": "fallback: status=down non-prod", "confidence": 0.7}
    if status in {"down", "degraded"}:
        return {"action": "notify", "action_input": {"channel": "ops", "message": f"fallback: {health.get('service')} status={status}"}, "reason": "fallback: notify", "confidence": 0.6}
    return {"action": "null", "action_input": {}, "reason": "fallback: healthy/unknown", "confidence": 0.5}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type(DecisionError),
)
def decide_with_llm(alert: Dict[str, Any], context: Dict[str, Any], diag: Optional[DiagnosticsContext] = None) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        if diag:
            diag.step("llm_skipped_no_key")
        return _fallback_decision(context)

    client = OpenAI()

    prompt = DECISION_PROMPT.format(
        alert_json=json.dumps(alert, ensure_ascii=False, indent=2),
        context_json=json.dumps(context, ensure_ascii=False, indent=2),
    )

    try:
        resp = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
            input=prompt,
            response_format={"type": "json_object"},
            timeout=20,
        )
        # responses API: טקסט JSON בתוך output_text
        txt = resp.output_text
        data = json.loads(txt)
        return data
    except Exception as e:
        if diag:
            diag.error("llm_decision", e)
        raise DecisionError(str(e))
