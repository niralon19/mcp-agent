# -*- coding: utf-8 -*-
"""Entry point פשוט להרצה מקומית."""

from __future__ import annotations
import json
import sys
from agent.agent import handle_alert

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <alert.json>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        alert = json.load(f)

    out = handle_alert(alert, context="")
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
