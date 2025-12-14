from __future__ import annotations

from fastapi import FastAPI, HTTPException
from typing import Any, Dict, List

from .store import DiagnosticsStore


def create_app(store: DiagnosticsStore) -> FastAPI:
    app = FastAPI(title="MCP Ops Agent - Diagnostics", version="1.0")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok"}

    @app.get("/diagnostics")
    def diagnostics(limit: int = 10) -> List[Dict[str, Any]]:
        return [ctx.summary() for ctx in store.last(limit)]

    @app.get("/diagnostics/{trace_id}")
    def diagnostics_trace(trace_id: str) -> Dict[str, Any]:
        ctx = store.get(trace_id)
        if not ctx:
            raise HTTPException(status_code=404, detail="trace_id not found")
        return {
            "summary": ctx.summary(),
            "steps": ctx.steps,
            "errors": ctx.errors,
        }

    return app
