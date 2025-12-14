def decide(alert, context):
    return {'action': 'restart_service' if alert.get('metric') == 'cpu' else 'escalate'}
