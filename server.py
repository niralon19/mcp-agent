from __future__ import annotations

import os
import threading
import uvicorn

from diagnostics.api import create_app
from diagnostics.store import DiagnosticsStore
from diagnostics.logging import setup_logging
from tools.registry import ToolRegistry

from tools.get_alerts import get_alerts
from tools.get_service_health import get_service_health
from tools.restart_service import restart_service
from tools.notify import notify

from agent.agent import OpsAgent


def build_tools() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register("get_alerts", get_alerts)
    tools.register("get_service_health", get_service_health)
    tools.register("restart_service", restart_service)
    tools.register("notify", notify)
    return tools


def main() -> None:
    setup_logging()

    diag_store = DiagnosticsStore(maxlen=int(os.getenv("DIAG_BUFFER", "200")))
    tools = build_tools()

    # Diagnostics API (FastAPI) - רץ בת'רד נפרד כדי לא לחסום לולאת Agent
    host = os.getenv("DIAG_HOST", "0.0.0.0")
    port = int(os.getenv("DIAG_PORT", "8088"))
    app = create_app(diag_store)

    def run_api():
        uvicorn.run(app, host=host, port=port, log_level="warning")

    t = threading.Thread(target=run_api, daemon=True)
    t.start()

    agent = OpsAgent(tools=tools, diag_store=diag_store)
    agent.run_forever()


if __name__ == "__main__":
    main()
