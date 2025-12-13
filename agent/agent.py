import time
from tools.get_alerts import get_alerts
from tools.restart_service import restart_service
from agent.context import build_context
from agent.decision import decide
from agent.policies import block_reason
from agent.memory import already_handled, mark_handled

POLL_INTERVAL = 30

def run_daemon():
    print("[AGENT] Running continuous Ops Agent")
    while True:
        alerts = get_alerts()
        for alert in alerts:
            if already_handled(alert["id"]):
                continue

            context = build_context(alert)
            if block_reason(alert, context):
                continue

            decision = decide(alert, context)

            if decision["action"] == "restart_service":
                restart_service(alert["service"])

            mark_handled(alert["id"])

        time.sleep(POLL_INTERVAL)
