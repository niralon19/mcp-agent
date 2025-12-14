from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from models import Alert
from tools.registry import ToolRegistry


@dataclass
class AgentContext:
    alert: Alert
    service_health: Dict[str, Any]
    notes: Dict[str, Any]


def build_context(alert: Alert, tools: ToolRegistry) -> AgentContext:
    health = tools.call("get_service_health", service=alert.service)
    notes = {
        "env": alert.labels.get("env", "unknown"),
        "service": alert.service,
        "severity": alert.severity,
    }
    return AgentContext(alert=alert, service_health=health, notes=notes)
