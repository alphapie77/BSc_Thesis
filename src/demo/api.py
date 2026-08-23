"""FastAPI entry point for the live thesis demonstration."""

from __future__ import annotations

from collections import OrderedDict
from functools import lru_cache
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.common.seed import set_seed
from src.demo.service import DemoError, DemoService

set_seed()

app = FastAPI(title="Audience Response Lab API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class GenerateRequest(BaseModel):
    plot: str = Field(min_length=1, max_length=6000)
    target_levels: list[int] = Field(min_length=1, max_length=2)
    request_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")


@lru_cache(maxsize=1)
def service() -> DemoService:
    return DemoService()


_cache: OrderedDict[str, dict] = OrderedDict()
_cache_lock = Lock()


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "backend_initialized": service.cache_info().currsize == 1,
        "verifier_b_loaded": False,
    }


@app.get("/api/ready")
def ready() -> dict:
    """Initialize every local artifact before declaring the demo ready."""
    try:
        demo = service()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Demo artifacts could not be initialized") from exc
    return {
        "status": "ready",
        "backend_initialized": True,
        "verifier_b_loaded": False,
        "rag": demo.cfg["rag"]["collection"],
    }


@app.post("/api/generate")
def generate(body: GenerateRequest) -> dict:
    with _cache_lock:
        cached = _cache.get(body.request_id)
        if cached is not None:
            return cached
    try:
        result = service().generate(
            plot=body.plot,
            target_levels=body.target_levels,
            request_id=body.request_id,
        )
    except DemoError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Live backend could not complete the request") from exc
    with _cache_lock:
        _cache[body.request_id] = result
        _cache.move_to_end(body.request_id)
        while len(_cache) > 128:
            _cache.popitem(last=False)
    return result
