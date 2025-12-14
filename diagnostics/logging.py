from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional


def setup_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter("%(message)s")

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)

    fh = logging.FileHandler("logs/agent.jsonl", encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)


def log_event(logger: logging.Logger, *, trace_id: Optional[str], event: str, data: Optional[Dict[str, Any]] = None, level: int = logging.INFO) -> None:
    payload = {
        "ts": datetime.utcnow().isoformat(),
        "trace_id": trace_id,
        "event": event,
        "data": data or {},
    }
    logger.log(level, json.dumps(payload, ensure_ascii=False))
