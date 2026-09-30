"""Structured, request-scoped logging.

Every analysis request emits one JSON line carrying the request id, the engine
route that was taken (rule / ml / retrieval / llm / fallback), latency and the
outcome — this is the observability the MVP Delivery Playbook asks for, and it
lets a reviewer confirm on the backend what the frontend displayed.
"""
from __future__ import annotations

import json
import logging
import sys
import uuid
from pathlib import Path

LOGGER_NAME = "p098"


def configure_logging(logs_dir: Path) -> logging.Logger:
    """Attach console + file handlers exactly once."""
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:  # already configured
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    logger.addHandler(stream)

    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(logs_dir / "app.log", encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        pass  # console logging still works if the file cannot be opened

    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def new_request_id() -> str:
    """Short, human-readable id used to correlate a request across layers."""
    return uuid.uuid4().hex[:12]


def log_request(request_id: str, route, latency_ms: float, outcome: str, extra: dict | None = None) -> None:
    payload = {
        "request_id": request_id,
        "route": route,
        "latency_ms": round(latency_ms, 1),
        "outcome": outcome,
    }
    if extra:
        payload.update(extra)
    get_logger().info("request %s", json.dumps(payload, ensure_ascii=False))


def emit_request_log(
    request_id: str,
    route,
    latency_ms: float,
    outcome: str,
    uncertain: bool = False,
    sarcasm: bool = False,
    confidence: float = 0.0,
    extra: dict | None = None,
) -> None:
    payload = {
        "request_id": request_id,
        "route": route,
        "latency_ms": round(latency_ms, 1),
        "outcome": outcome,
        "uncertain": uncertain,
        "sarcasm": sarcasm,
        "confidence": round(confidence, 3),
    }
    if extra:
        payload.update(extra)
    get_logger().info("request %s", json.dumps(payload, ensure_ascii=False))

