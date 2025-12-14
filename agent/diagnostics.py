from tools.get_service_health import get_service_health
from tools.fetch_logs import fetch_logs
from tools.check_db_connections import check_db_connections
from tools.fetch_disk_usage import fetch_disk_usage

DIAGNOSTIC_FUNCS = {
    'service_health': lambda a: get_service_health(a['service']),
    'logs': lambda a: fetch_logs(a['service'], lines=100),
    'db_connections': lambda a: check_db_connections(a['service']),
    'disk_usage': lambda a: fetch_disk_usage(a['service']),
}

def run_diagnostics(alert, playbook):
    results = {}
    if not playbook:
        return results

    for diag in playbook.get('diagnostics', []):
        try:
            results[diag] = DIAGNOSTIC_FUNCS[diag](alert)
        except Exception as e:
            results[diag] = f'error: {e}'

    return results
