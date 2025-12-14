from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Alert:
    """ייצוג בסיסי של התראה שמגיעה ממערכת ניטור (Grafana/Prometheus/PagerDuty וכו')."""
    id: str
    name: str
    severity: str = "warning"  # info|warning|critical
    service: str = "unknown"
    summary: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    starts_at: Optional[datetime] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity,
            "service": self.service,
            "summary": self.summary,
            "labels": self.labels,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "raw": self.raw,
        }
