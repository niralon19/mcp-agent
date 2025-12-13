from tools.get_service_health import get_service_health
from agent.memory import load_memory
from agent.learning import summarize_memory

def build_context(alert):
    memory = load_memory()
    learned = summarize_memory(memory)

    return {
        "alert": alert,
        "service_health": get_service_health(alert["service"]),
        "learned_patterns": learned,
        "allowed_actions": ["restart_service", "notify", "escalate"]
    }
