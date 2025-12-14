from __future__ import annotations

import random
from typing import Dict


def get_service_health(service: str) -> Dict[str, str]:
    """דמו: בדיקת 'בריאות'. בפועל - curl, systemctl, k8s API וכו'."""
    # אקראי לצורך דמו
    status = random.choice(["healthy", "degraded", "down"])
    return {"service": service, "status": status}
