def get_alerts():
    return [
        {
            "id": "cpu_high_1",
            "severity": "warning",
            "service": "billing-api",
            "metric": "cpu",
            "value": 92,
            "threshold": 85,
            "timestamp": "2025-01-12T10:00:00"
        }
    ]
