from __future__ import annotations

from typing import Dict


def restart_service(service: str) -> Dict[str, str]:
    """דמו: הפעלה מחדש. בפועל - systemctl/k8s rollout restart/Ansible וכו'."""
    return {"service": service, "action": "restart", "result": "ok"}
