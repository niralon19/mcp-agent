from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict


STATE_DIR = os.getenv("STATE_DIR", "state")
STATE_FILE = os.path.join(STATE_DIR, "memory.json")


@dataclass
class Memory:
    handled_alert_ids: set[str]

    @classmethod
    def load(cls) -> "Memory":
        os.makedirs(STATE_DIR, exist_ok=True)
        if not os.path.exists(STATE_FILE):
            return cls(handled_alert_ids=set())
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(handled_alert_ids=set(data.get("handled_alert_ids", [])))

    def save(self) -> None:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"handled_alert_ids": sorted(self.handled_alert_ids)}, f, ensure_ascii=False, indent=2)

    def already_handled(self, alert_id: str) -> bool:
        return alert_id in self.handled_alert_ids

    def mark_handled(self, alert_id: str) -> None:
        self.handled_alert_ids.add(alert_id)
