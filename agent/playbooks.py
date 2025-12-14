PLAYBOOKS = {
    'cpu': {
        'auto_restart': True,
        'diagnostics': ['logs', 'service_health']
    },
    'db': {
        'auto_restart': False,
        'diagnostics': ['db_connections']
    },
    'disk': {
        'auto_restart': False,
        'diagnostics': ['disk_usage']
    }
}
