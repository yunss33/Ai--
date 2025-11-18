#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 加载 src/.env（参考 Agent 项目做法）
try:
    from dotenv import load_dotenv  # type: ignore

    src_env = Path(__file__).resolve().parent / ".env"
    if src_env.exists():
        load_dotenv(str(src_env))
except Exception:
    pass

# 从内部应用模块导入 FastAPI 实例
from app.main import app as _app  # noqa: E402

app: FastAPI = _app


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_list(name: str, default: List[str]) -> List[str]:
    raw = os.environ.get(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


_cors_allow_origins = _env_list("CORS_ORIGINS", ["*"])
_cors_allow_methods = _env_list("CORS_ALLOW_METHODS", ["*"])
_cors_allow_headers = _env_list("CORS_ALLOW_HEADERS", ["*"])
_cors_expose_headers = _env_list("CORS_EXPOSE_HEADERS", [])
_cors_allow_credentials = _env_bool("CORS_ALLOW_CREDENTIALS", False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins,
    allow_methods=_cors_allow_methods,
    allow_headers=_cors_allow_headers,
    expose_headers=_cors_expose_headers,
    allow_credentials=_cors_allow_credentials,
)


@app.get("/")
async def root() -> dict:
    return {"success": True, "status": "ok"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("PORT") or os.getenv("API_PORT", "8880"))
    except Exception:
        port = 8880
    uvicorn.run(app, host=host, port=port)


def run(host: str | None = None, port: int | None = None) -> None:
    """控制台入口，便于使用 `python -m main` 启动 API。"""
    import uvicorn

    host_eff = host or os.getenv("API_HOST", "0.0.0.0")
    try:
        port_eff = int(
            port if port is not None else (os.getenv("PORT") or os.getenv("API_PORT", "8880")),
        )
    except Exception:
        port_eff = 8880
    uvicorn.run(app, host=host_eff, port=port_eff)

