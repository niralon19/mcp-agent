# -*- coding: utf-8 -*-
"""Diagnostics רזה: Trace לכל Alert + צעדים + שגיאות.

המטרה: שקיפות ודיבוג, בלי להכביד על הארכיטקטורה.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Diagnostics:
    alert: Dict[str, Any]
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: str = field(default_factory=_utc_iso)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None

    def step(self, name: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.steps.append({
            "time": _utc_iso(),
            "step": name,
            "data": data or {},
        })

    def fail(self, err: Exception, source: str = "agent") -> None:
        self.error = f"{source}: {err}"

    def summary(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "started_at": self.started_at,
            "alert": self.alert,
            "steps": self.steps,
            "error": self.error,
        }
