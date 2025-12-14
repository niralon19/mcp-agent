from __future__ import annotations

from typing import Any, Callable, Dict


class ToolRegistry:
    """Registry פשוט שמדמה MCP tools (בפועל - אצלך זה יכול להיות קריאה לשרת MCP)."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = fn

    def has(self, name: str) -> bool:
        return name in self._tools

    def call(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name](**kwargs)

    def list(self) -> Dict[str, Callable[..., Any]]:
        return dict(self._tools)
