from datetime import datetime

def policy_allows(alert: dict, action_name: str) -> bool:
    # דוגמה לפוליסי פשוטה וברורה

    # Critical – אין autorun
    if alert.get("severity") == "critical":
        return False

    # בלילה (22-06) – אין restart
    hour = datetime.utcnow().hour
    if action_name == "restart_service" and (hour >= 22 or hour < 6):
        return False

    return True
