def block_reason(alert, context):
    if alert["severity"] == "critical":
        return True
    return False
