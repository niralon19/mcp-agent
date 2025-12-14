from __future__ import annotations

import os
import re
import yaml
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from models import Alert
from tools.registry import ToolRegistry
from diagnostics.context import DiagnosticsContext


@dataclass
class PlaybookMatch:
    playbook_id: str
    playbook: Dict[str, Any]


def _render_template(value: Any, *, alert: Alert, ctx: Dict[str, Any]) -> Any:
    if isinstance(value, str):
        # תבניות פשוטות: {{alert.service}}, {{alert.id}}
        def repl(m):
            expr = m.group(1).strip()
            if expr.startswith("alert."):
                key = expr.split(".", 1)[1]
                return str(getattr(alert, key, ""))
            if expr.startswith("ctx."):
                # ctx.service_health.status וכו'
                path = expr.split(".", 1)[1]
                cur: Any = ctx
                for part in path.split("."):
                    if isinstance(cur, dict):
                        cur = cur.get(part)
                    else:
                        cur = getattr(cur, part, None)
                return "" if cur is None else str(cur)
            return m.group(0)

        return re.sub(r"\{\{([^}]+)\}\}", repl, value)

    if isinstance(value, dict):
        return {k: _render_template(v, alert=alert, ctx=ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [_render_template(v, alert=alert, ctx=ctx) for v in value]
    return value


def load_playbooks(dir_path: str = "playbooks") -> Dict[str, Dict[str, Any]]:
    books: Dict[str, Dict[str, Any]] = {}
    if not os.path.isdir(dir_path):
        return books
    for fn in os.listdir(dir_path):
        if not fn.endswith(".yaml") and not fn.endswith(".yml"):
            continue
        path = os.path.join(dir_path, fn)
        with open(path, "r", encoding="utf-8") as f:
            pb = yaml.safe_load(f)
        if pb and "id" in pb:
            books[pb["id"]] = pb
    return books


def match_playbook(alert: Alert, playbooks: Dict[str, Dict[str, Any]]) -> Optional[PlaybookMatch]:
    for pb_id, pb in playbooks.items():
        m = pb.get("match", {}) or {}
        if m.get("alert_name") and m["alert_name"] == alert.name:
            return PlaybookMatch(playbook_id=pb_id, playbook=pb)
    return None


def _get_path(data: Dict[str, Any], path: str) -> Any:
    # path: "ctx.service_health.status"
    cur: Any = data
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
    return cur


def _eval_when(when: Dict[str, Any], runtime: Dict[str, Any]) -> bool:
    # תומך כרגע: equals: {path,value}
    if "equals" in when:
        eq = when["equals"]
        actual = _get_path(runtime, eq["path"])
        return str(actual).lower() == str(eq["value"]).lower()
    return False


def run_playbook(match: PlaybookMatch, *, alert: Alert, tools: ToolRegistry, diag: DiagnosticsContext) -> Tuple[bool, Dict[str, Any]]:
    pb = match.playbook
    diag.playbook_id = match.playbook_id
    diag.step("playbook_selected", {"playbook_id": match.playbook_id})

    runtime_ctx: Dict[str, Any] = {"service_health": None}
    runtime = {"alert": alert.to_dict(), "ctx": runtime_ctx}

    for idx, step in enumerate(pb.get("steps", []) or []):
        diag.step("playbook_step_start", {"index": idx, "step": step})

        if "check" in step:
            spec = step["check"]
            tool = spec["tool"]
            inp = _render_template(spec.get("input", {}), alert=alert, ctx=runtime)
            out = tools.call(tool, **inp)
            runtime_ctx["service_health"] = out
            runtime["ctx"] = runtime_ctx
            diag.step("check_result", {"tool": tool, "input": inp, "output": out})
            continue

        if "action" in step:
            spec = step["action"]
            tool = spec["tool"]
            inp = _render_template(spec.get("input", {}), alert=alert, ctx=runtime)
            out = tools.call(tool, **inp)
            diag.step("action_result", {"tool": tool, "input": inp, "output": out})
            continue

        if "decide" in step:
            spec = step["decide"]
            when = spec.get("when", {}) or {}
            ok = _eval_when(when, runtime)
            branch = "then" if ok else "else"
            diag.step("decision_branch", {"branch": branch, "when": when})

            for inner in spec.get(branch, []) or []:
                if "action" in inner:
                    a = inner["action"]
                    tool = a["tool"]
                    inp = _render_template(a.get("input", {}), alert=alert, ctx=runtime)
                    out = tools.call(tool, **inp)
                    diag.step("action_result", {"tool": tool, "input": inp, "output": out})
                if "verify" in inner:
                    v = inner["verify"]
                    tool = v["tool"]
                    inp = _render_template(v.get("input", {}), alert=alert, ctx=runtime)
                    out = tools.call(tool, **inp)
                    runtime_ctx["service_health"] = out
                    runtime["ctx"] = runtime_ctx
                    diag.step("verify_result", {"tool": tool, "input": inp, "output": out})
            continue

        diag.step("playbook_step_unknown", {"index": idx})

    diag.step("playbook_completed", {"playbook_id": match.playbook_id})
    return True, runtime
