def allow(decision, min_conf=0.75):
    if decision.recommendation != "run_action":
        return False
    if decision.confidence < min_conf:
        return False
    if any(a.risk != "low" for a in decision.actions):
        return False
    return True
