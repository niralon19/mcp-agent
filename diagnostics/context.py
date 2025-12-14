from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
import traceback


@dataclass
class DiagnosticsContext:
    """אובייקט Trace שמלווה טיפול ב-Alert מקצה לקצה."""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: Optional[str] = None
    playbook_id: Optional[str] = None
    started_at: datetime = field(default_factory=lambda: datetime.utcnow())
    steps: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def step(self, name: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.steps.append({
            "ts": datetime.utcnow().isoformat(),
            "step": name,
            "data": data or {},
        })

    def error(self, source: str, exc: BaseException) -> None:
        self.errors.append({
            "ts": datetime.utcnow().isoformat(),
            "source": source,
            "error": str(exc),
            "traceback": traceback.format_exc(limit=25),
        })

    def summary(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "alert_id": self.alert_id,
            "playbook_id": self.playbook_id,
            "started_at": self.started_at.isoformat(),
            "steps_count": len(self.steps),
            "errors_count": len(self.errors),
            "last_step": self.steps[-1]["step"] if self.steps else None,
        }
