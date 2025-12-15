def check_health(service: str):
    return {"status": "degraded"}

def tail_logs(service: str):
    return ["error: timeout", "warning: slow response"]

def restart_service(service: str):
    return f"service {service} restarted"

TOOLS = {
    "check_health": check_health,
    "tail_logs": tail_logs,
    "restart_service": restart_service,
}
