import json
from pathlib import Path

STATE_FILE = Path("agent_state.json")

def load_memory():
    if not STATE_FILE.exists():
        return []
    return json.loads(STATE_FILE.read_text())

def already_handled(alert_id):
    return alert_id in load_memory()

def mark_handled(alert_id):
    memory = load_memory()
    memory.append(alert_id)
    STATE_FILE.write_text(json.dumps(memory, indent=2))
