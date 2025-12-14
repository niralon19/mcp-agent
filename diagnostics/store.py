from __future__ import annotations

from collections import deque
from threading import Lock
from typing import List, Optional

from .context import DiagnosticsContext


class DiagnosticsStore:
    """Ring-buffer של traces בזיכרון (100 אחרונים כברירת מחדל)."""

    def __init__(self, maxlen: int = 200) -> None:
        self._buf = deque(maxlen=maxlen)
        self._lock = Lock()

    def add(self, ctx: DiagnosticsContext) -> None:
        with self._lock:
            self._buf.append(ctx)

    def last(self, n: int = 10) -> List[DiagnosticsContext]:
        with self._lock:
            return list(self._buf)[-n:]

    def get(self, trace_id: str) -> Optional[DiagnosticsContext]:
        with self._lock:
            for ctx in reversed(self._buf):
                if ctx.trace_id == trace_id:
                    return ctx
        return None
