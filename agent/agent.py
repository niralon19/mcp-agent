import time
from tools.get_alerts import get_alerts
from tools.restart_service import restart_service
from tools.notify import notify
from agent.context import build_context
from agent.decision import decide
from agent.policies import block_reason
from agent.memory import already_handled, mark_handled
from agent.diagnostics import run_diagnostics
from agent.playbooks import PLAYBOOKS

POLL_INTERVAL = 30

def run_daemon():
    print('[AGENT] Running continuous Ops Agent')
    while True:
        alerts = get_alerts()
        for alert in alerts:
            if already_handled(alert['id']):
                continue

            context = build_context(alert)
            if block_reason(alert, context):
                continue

            decision = decide(alert, context)
            playbook = PLAYBOOKS.get(alert.get('metric'))

            if decision['action'] == 'restart_service' and playbook and playbook.get('auto_restart'):
                restart_service(alert['service'])

            elif decision['action'] == 'escalate':
                diagnostics = run_diagnostics(alert, playbook)
                notify(alert, diagnostics)

            mark_handled(alert['id'])

        time.sleep(POLL_INTERVAL)
