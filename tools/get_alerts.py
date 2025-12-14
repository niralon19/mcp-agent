from __future__ import annotations

import os
import time
from typing import List
from datetime import datetime
from models import Alert


def get_alerts() -> List[Alert]:
    """דמו: מחזיר התראות 'מזוייפות'. בפרודקשן תחליף לקריאה ל-Grafana/Alertmanager/PagerDuty."""
    demo = os.getenv("DEMO_MODE", "1") == "1"
    if not demo:
        return []

    # כל ~30 שניות תן התראה אחת (כדי שתראה את הלולאה עובדת).
    if int(time.time()) % 30 != 0:
        return []

    return [
        Alert(
            id=f"demo-{int(time.time())}",
            name=os.getenv("DEMO_ALERT_NAME", "ServiceDown"),
            severity=os.getenv("DEMO_SEVERITY", "warning"),
            service=os.getenv("DEMO_SERVICE", "nginx"),
            summary="Demo alert generated locally",
            labels={"env": os.getenv("ENV", "dev")},
            starts_at=datetime.utcnow(),
            raw={"source": "demo"},
        )
    ]
