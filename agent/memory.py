import json
from pathlib import Path

STATE_FILE = Path('agent_state.json')

def _load():
    if not STATE_FILE.exists():
        return []
    return json.loads(STATE_FILE.read_text())

def already_handled(alert_id):
    return alert_id in _load()

def mark_handled(alert_id):
    data = _load()
    data.append(alert_id)
    STATE_FILE.write_text(json.dumps(data, indent=2))
