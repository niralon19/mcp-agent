from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from models import Alert


PROTECTED_SERVICES = {"payments", "auth", "core-db"}


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    escalate: bool = False


def evaluate_policies(alert: Alert) -> PolicyDecision:
    # 1) קריטי -> להסלים (ברירת מחדל זהירה)
    if alert.severity.lower() == "critical":
        return PolicyDecision(False, "התראה Critical -> הסלמה לאדם", escalate=True)

    # 2) שירותים רגישים
    if alert.service in PROTECTED_SERVICES:
        return PolicyDecision(False, f"שירות מוגן ({alert.service}) -> לא מבצע פעולות אוטומטיות", escalate=True)

    # 3) env=prod + פעולה מסוכנת? (נבדק בהמשך לפני action)
    return PolicyDecision(True, "מאושר ע"י policies")
