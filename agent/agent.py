from __future__ import annotations

import os
import time
import logging
from typing import Any, Dict, Optional

from models import Alert
from tools.registry import ToolRegistry
from diagnostics.context import DiagnosticsContext
from diagnostics.store import DiagnosticsStore
from diagnostics.logging import log_event

from .memory import Memory
from .policies import evaluate_policies
from .context import build_context
from .decision import decide_with_llm
from .playbook_engine import load_playbooks, match_playbook, run_playbook


logger = logging.getLogger("mcp_ops_agent")


class OpsAgent:
    def __init__(self, tools: ToolRegistry, diag_store: DiagnosticsStore) -> None:
        self.tools = tools
        self.diag_store = diag_store
        self.memory = Memory.load()
        self.playbooks = load_playbooks()

    def handle_alert(self, alert: Alert) -> None:
        diag = DiagnosticsContext(alert_id=alert.id)
        self.diag_store.add(diag)

        log_event(logger, trace_id=diag.trace_id, event="alert_received", data=alert.to_dict())
        diag.step("alert_received", alert.to_dict())

        # Idempotency
        if self.memory.already_handled(alert.id):
            diag.step("skipped_already_handled", {"alert_id": alert.id})
            log_event(logger, trace_id=diag.trace_id, event="alert_skipped_already_handled", data={"alert_id": alert.id})
            return

        # Policies
        pol = evaluate_policies(alert)
        diag.step("policy_evaluated", {"allowed": pol.allowed, "reason": pol.reason, "escalate": pol.escalate})
        if not pol.allowed:
            # notify + mark handled (כדי לא להציף)
            self.tools.call("notify", channel="ops", message=f"Policy block: {pol.reason} | alert={alert.name} service={alert.service}")
            diag.step("policy_block_notify_sent")
            self.memory.mark_handled(alert.id)
            self.memory.save()
            return

        # 1) Playbook path (מועדף)
        pb_match = match_playbook(alert, self.playbooks)
        if pb_match:
            try:
                ok, runtime = run_playbook(pb_match, alert=alert, tools=self.tools, diag=diag)
                diag.step("playbook_runtime", {"runtime_ctx": runtime.get("ctx")})
                self.memory.mark_handled(alert.id)
                self.memory.save()
                log_event(logger, trace_id=diag.trace_id, event="playbook_handled", data={"playbook_id": pb_match.playbook_id, "ok": ok})
                return
            except Exception as e:
                diag.error("playbook_execution", e)
                log_event(logger, trace_id=diag.trace_id, event="playbook_failed", data={"error": str(e)}, level=logging.ERROR)

        # 2) LLM fallback path (אם אין playbook / playbook נכשל)
        try:
            ctx_obj = build_context(alert, self.tools)
            ctx: Dict[str, Any] = {
                "service_health": ctx_obj.service_health,
                "notes": ctx_obj.notes,
            }
            diag.step("context_built", ctx)

            decision = decide_with_llm(alert.to_dict(), ctx, diag=diag)
            diag.step("llm_decision", decision)
            log_event(logger, trace_id=diag.trace_id, event="llm_decision", data=decision)

            action = decision.get("action")
            action_input = decision.get("action_input") or {}

            # Safety: PROD restart requires confidence threshold
            env = (ctx.get("notes") or {}).get("env", "unknown")
            if env == "prod" and action == "restart_service":
                conf = float(decision.get("confidence") or 0.0)
                if conf < float(os.getenv("PROD_RESTART_MIN_CONF", "0.85")):
                    diag.step("prod_restart_blocked_low_confidence", {"confidence": conf})
                    self.tools.call("notify", channel="ops", message=f"נחסם restart ב-PROD בגלל confidence נמוך ({conf}). alert={alert.name} service={alert.service}")
                    action = "notify"
                    action_input = {"channel": "ops", "message": "נדרש אישור אדם לריסטארט ב-PROD."}

            if action and action != "null":
                diag.step("action_execute", {"tool": action, "input": action_input})
                out = self.tools.call(action, **action_input)
                diag.step("action_done", {"output": out})
                log_event(logger, trace_id=diag.trace_id, event="action_done", data={"tool": action, "output": out})
            else:
                diag.step("no_action")
                log_event(logger, trace_id=diag.trace_id, event="no_action", data={})

            self.memory.mark_handled(alert.id)
            self.memory.save()

        except Exception as e:
            diag.error("handle_alert", e)
            log_event(logger, trace_id=diag.trace_id, event="handle_alert_failed", data={"error": str(e)}, level=logging.ERROR)
            # escalation
            try:
                self.tools.call("notify", channel="ops", message=f"Agent exception. trace={diag.trace_id} error={e}")
            except Exception:
                pass

    def run_forever(self) -> None:
        poll = float(os.getenv("POLL_SECONDS", "5"))
        while True:
            alerts = self.tools.call("get_alerts")
            for a in alerts:
                self.handle_alert(a)
            time.sleep(poll)
