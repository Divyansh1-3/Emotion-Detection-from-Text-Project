"""Application configuration, loaded from environment variables (.env).

A single :class:`Settings` dataclass carries every tunable value used across the
app.  Values are read from the process environment at call time, so tests can
override them via ``os.environ`` before calling :func:`get_settings`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# .../p098-emotion-detection-text-divya  (config.py is at backend/app/core/config.py)
ROOT = Path(__file__).resolve().parents[3]


def _bool(name: str, default: str = "1") -> bool:
    return os.getenv(name, default).strip().lower() not in ("0", "false", "no", "")


def _float(name: str, default: str) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)


def _int(name: str, default: str) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)


@dataclass
class Settings:
    """Typed view over the environment configuration."""

    # ---- LLM (OpenAI-compatible) -------------------------------------------
    llm_mode: str = "mock"                 # "api" | "mock"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 20.0
    llm_max_tokens: int = 200

    # ---- Pretrained models --------------------------------------------------
    emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"
    sarcasm_model: str = "helinivan/english-sarcasm-detector"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    use_models: bool = True                # False -> heuristic/TF-IDF fallback (tests, offline)

    # ---- Decision thresholds ------------------------------------------------
    uncertain_threshold: float = 0.40
    sarcasm_threshold: float = 0.50
    retrieval_top_k: int = 5

    # ---- Storage ------------------------------------------------------------
    database_url: str = "sqlite:///emotion.sqlite3"

    # ---- Server -------------------------------------------------------------
    flask_host: str = "127.0.0.1"
    flask_port: int = 5000
    max_input_chars: int = 4000
    max_batch_rows: int = 500

    # ---- Derived paths ------------------------------------------------------
    root: Path = field(default=ROOT)

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def kb_dir(self) -> Path:
        return self.data_dir / "kb"

    @property
    def index_dir(self) -> Path:
        return self.root / "index"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def prompts_dir(self) -> Path:
        return self.root / "prompts"

    @property
    def llm_enabled(self) -> bool:
        """True only when the app should actually call an external LLM."""
        return self.llm_mode.lower() == "api" and bool(self.openai_api_key.strip())

    @property
    def sqlite_path(self) -> Path:
        """Absolute SQLite path parsed from ``database_url`` (sqlite:///...)."""
        url = self.database_url
        if url.startswith("sqlite:///"):
            raw = url[len("sqlite:///"):]
            p = Path(raw)
            return p if p.is_absolute() else (self.root / raw)
        # Non-sqlite backends are a documented config swap; default file otherwise.
        return self.root / "emotion.sqlite3"


def get_settings() -> Settings:
    """Build a :class:`Settings` from the current environment.

    Cheap enough to call freely.  ``load_dotenv`` does not override variables
    that are already set, so test-provided ``os.environ`` values win.
    """
    load_dotenv(ROOT / ".env", override=False)
    return Settings(
        llm_mode=os.getenv("LLM_MODE", "mock"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        llm_timeout_seconds=_float("LLM_TIMEOUT_SECONDS", "20"),
        llm_max_tokens=_int("LLM_MAX_TOKENS", "200"),
        emotion_model=os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base"),
        sarcasm_model=os.getenv("SARCASM_MODEL", "helinivan/english-sarcasm-detector"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        use_models=_bool("USE_MODELS", "1"),
        uncertain_threshold=_float("UNCERTAIN_THRESHOLD", "0.40"),
        sarcasm_threshold=_float("SARCASM_THRESHOLD", "0.50"),
        retrieval_top_k=_int("RETRIEVAL_TOP_K", "5"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///emotion.sqlite3"),
        flask_host=os.getenv("FLASK_HOST", "127.0.0.1"),
        flask_port=_int("FLASK_PORT", "5000"),
        max_input_chars=_int("MAX_INPUT_CHARS", "4000"),
        max_batch_rows=_int("MAX_BATCH_ROWS", "500"),
    )
