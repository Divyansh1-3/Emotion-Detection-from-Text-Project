"""Optional post-hoc temperature scaling with a versioned fitted profile."""
from __future__ import annotations

import hashlib
import json
import math
import os
from functools import lru_cache
from pathlib import Path

from backend.app.core.config import ROOT, get_settings
from backend.app.domain.emotion_schema import EMOTION_LABELS


def temperature_scale(scores: dict[str, float], temperature: float) -> dict[str, float]:
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("Temperature must be finite and positive")
    logits = {label: math.log(max(float(scores.get(label, 0)), 1e-12)) / temperature for label in EMOTION_LABELS}
    peak = max(logits.values())
    values = {label: math.exp(logit - peak) for label, logit in logits.items()}
    total = sum(values.values())
    return {label: value / total for label, value in values.items()}


@lru_cache(maxsize=1)
def pipeline_fingerprint() -> str:
    digest = hashlib.sha256()
    files = [f"backend/app/engines/{name}.py" for name in
             ("router", "fusion", "rules", "preprocess", "language_support", "emotion_model", "sarcasm_model", "retrieval", "calibration")]
    files += ["data/kb/emotions.jsonl", "data/kb/exemplars.jsonl"]
    for filename in files:
        digest.update(filename.encode())
        # Git's platform line-ending conversion must not invalidate the profile.
        digest.update((ROOT / filename).read_text(encoding="utf-8").replace("\r\n", "\n").encode())
    return digest.hexdigest()


def configuration_signature() -> dict:
    settings = get_settings()
    return {"emotion_model": settings.emotion_model, "sarcasm_model": settings.sarcasm_model,
            "embedding_model": settings.embedding_model, "retrieval_top_k": settings.retrieval_top_k,
            "sarcasm_threshold": settings.sarcasm_threshold}


@lru_cache(maxsize=4)
def _read_profile(path: str, modified: int) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def calibration_profile() -> tuple[dict | None, str]:
    if os.getenv("CALIBRATION_ENABLED", "1").lower() in {"0", "false", "no"}:
        return None, "disabled"
    path = Path(os.getenv("CALIBRATION_FILE", str(ROOT / "data/calibration/temperature.json")))
    try:
        profile = _read_profile(str(path), path.stat().st_mtime_ns)
        temperature = float(profile["temperature"])
        if profile.get("schema_version") != 1 or not math.isfinite(temperature) or not 0.1 <= temperature <= 10:
            return None, "invalid"
        if profile.get("pipeline_fingerprint") != pipeline_fingerprint() or profile.get("configuration") != configuration_signature():
            return None, "incompatible"
        if not profile.get("validation_passed"):
            return None, "validation_not_passed"
        return profile, "temperature_scaled"
    except FileNotFoundError:
        return None, "not_fitted"
    except (OSError, ValueError, TypeError, KeyError):
        return None, "invalid"


def calibrate_scores(scores: dict[str, float], eligible: bool) -> tuple[dict[str, float], str]:
    if eligible:
        profile, status = calibration_profile()
        if profile is not None:
            return temperature_scale(scores, profile["temperature"]), status
    return scores, "uncalibrated_fusion"
