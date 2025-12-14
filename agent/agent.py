# -*- coding: utf-8 -*-
"""Agent רזה: Alert -> LLM decide -> (Playbook guardrail) -> Tool -> Notify/Store."""

from __future__ import annotations
import os
import time
from typing import Any, Dict, Optional

from .diagnostics import Diagnostics
from .decision import decide
from .playbook import is_action_allowed
from .tools import restart_service, notify, save_diagnostics_jsonl

def _incident_summary(alert, action, diag):
    return f"[{diag.trace_id}] action={action} alert={alert.get('alert_name') or alert.get('metric')}"


def handle_alert(alert: Dict[str, Any], *, context: str = "") -> Dict[str, Any]:
    diag = Diagnostics(alert)
    diag.step("alert_received")

    try:
        decision = decide(alert, context=context, diag=diag)
        action = (decision.get("action") or "").strip()
        diag.step("decision_received", {"action": action, "confidence": decision.get("confidence")})

        # Confidence gate: החלטה עם ביטחון נמוך מסלימה
        conf = decision.get("confidence", 1)
        if conf is not None and conf < float(os.getenv("CONFIDENCE_MIN", "0.6")):
            diag.step("low_confidence_escalate", {"confidence": conf})
            notify(alert, reason="low_confidence", diagnostics=diag.summary())
            diag.step("incident_summary", {"summary": _incident_summary(alert, action, diag)})
            return diag.summary()

        if action == "restart_service" and not is_action_allowed(alert, action):
            diag.step("action_blocked_by_playbook", {"action": action})
            notify(alert, reason="blocked_by_playbook", diagnostics=diag.summary())
            diag.step("incident_summary", {"summary": _incident_summary(alert, action, diag)})
            return diag.summary()

        if action == "restart_service":
            service = alert.get("service")
            diag.step("tool_restart_service_start", {"service": service})

            retries = int(os.getenv("TOOL_RETRIES", "2"))
            last_err: Optional[Exception] = None
            for attempt in range(1, retries + 1):
                try:
                    result = restart_service(service)
                    diag.step("tool_restart_service_ok", {"result": result, "attempt": attempt})
                    break
                except Exception as e:
                    last_err = e
                    diag.step("tool_restart_service_fail", {"attempt": attempt, "error": str(e)})
                    time.sleep(0.5 * attempt)
            else:
                raise last_err or RuntimeError("restart_service failed")

            diag.step("incident_summary", {"summary": _incident_summary(alert, action, diag)})
            return diag.summary()

        if action in ("escalate", ""):
            diag.step("escalate")
            notify(alert, reason="escalate", diagnostics=diag.summary())
            diag.step("incident_summary", {"summary": _incident_summary(alert, action, diag)})
            return diag.summary()

        if action == "ignore":
            diag.step("ignored")
            diag.step("incident_summary", {"summary": _incident_summary(alert, action, diag)})
            return diag.summary()

        diag.step("unknown_action", {"action": action})
        notify(alert, reason="unknown_action", diagnostics=diag.summary())
        return diag.summary()

    except Exception as e:
        diag.fail(e, source="handle_alert")
        notify(alert, reason="exception", diagnostics=diag.summary())
        return diag.summary()
    finally:
        path = os.getenv("DIAGNOSTICS_JSONL", "")
        if path:
            try:
                save_diagnostics_jsonl(path, diag.summary())
            except Exception:
                pass
