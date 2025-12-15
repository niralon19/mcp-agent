from noc_agent.logging_utils import logger, cid
from noc_agent.tools import TOOLS
from noc_agent.decision import decide
from noc_agent.guardrails import allow
from noc_agent.policy import policy_allows
from noc_agent.memory import Memory

log = logger()
memory = Memory(ttl_seconds=300)

def handle_alert(alert: dict):
    _cid = cid()
    log.info(f"[{_cid}] alert for {alert['service']}")

    # בדקתי
    context = {
        "health": TOOLS["check_health"](alert["service"]),
        "logs": TOOLS["tail_logs"](alert["service"]),
    }

    # החלטתי
    decision = decide(alert, context, list(TOOLS.keys()))

    if not allow(decision):
        log.info(f"[{_cid}] blocked by guardrails")
        return {"status": "closed", "reason": decision.close_message}

    results = []
    for action in decision.actions:
        key = f"{alert['service']}:{action.name}"

        if memory.seen_recently(key):
            log.warning(f"[{_cid}] skipped {action.name} (recently executed)")
            continue

        if not policy_allows(alert, action.name):
            log.warning(f"[{_cid}] blocked by policy: {action.name}")
            continue

        fn = TOOLS.get(action.name)
        if fn:
            out = fn(**action.args)
            memory.mark(key)
            results.append({action.name: out})

    if results:
        log.info(f"[{_cid}] handled automatically")
        return {"status": "handled", "results": results}

    log.info(f"[{_cid}] nothing executed")
    return {"status": "closed", "reason": decision.close_message}
