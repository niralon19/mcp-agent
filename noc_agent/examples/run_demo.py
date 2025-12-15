from noc_agent.app import handle_alert

alert = {
    "service": "orders-api",
    "severity": "warning",
    "description": "Latency גבוהה",
    "timestamp": "2025-12-15T00:00:00Z"
}

print(handle_alert(alert))
