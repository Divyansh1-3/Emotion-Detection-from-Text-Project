"""Emotion ML engine — pretrained transformer with a heuristic fallback.

Primary path: a Hugging Face ``text-classification`` pipeline over the 7-label
DistilRoBERTa emotion model (loaded lazily as a process singleton to keep the
8 GB-RAM footprint low).  If ``use_models`` is off or the weights cannot be
loaded (offline / not downloaded yet), it falls back to the rule lexicon so the
pipeline always returns a full distribution over EMOTION_LABELS.
"""
from __future__ import annotations

import threading

from backend.app.core.config import get_settings
from backend.app.domain.emotion_schema import EMOTION_LABELS
from backend.app.engines.rules import analyze_rules

_lock = threading.Lock()
_pipeline = None
_load_failed = False


def _load_pipeline(model_name: str):
    global _pipeline, _load_failed
    if _pipeline is not None or _load_failed:
        return _pipeline
    with _lock:
        if _pipeline is not None or _load_failed:
            return _pipeline
        try:
            from transformers import pipeline
            try:
                _pipeline = pipeline("text-classification", model=model_name, top_k=None, model_kwargs={"local_files_only": True})
            except Exception:
                _pipeline = pipeline("text-classification", model=model_name, top_k=None)
        except Exception:
            _load_failed = True
            _pipeline = None
    return _pipeline


def _normalise(dist: dict[str, float]) -> dict[str, float]:
    total = sum(dist.values())
    if total <= 0:
        dist = {label: (1.0 if label == "neutral" else 0.0) for label in EMOTION_LABELS}
        total = 1.0
    return {label: round(dist.get(label, 0.0) / total, 4) for label in EMOTION_LABELS}


def _heuristic(text: str) -> dict[str, float]:
    hint = analyze_rules(text).emotion_hint
    if not hint:
        return _normalise({"neutral": 1.0})
    return _normalise({label: hint.get(label, 0.0) for label in EMOTION_LABELS})


def predict_emotions(text: str) -> tuple[dict[str, float], str]:
    """Return (distribution over the 7 labels, backend used: 'transformer'|'heuristic')."""
    settings = get_settings()
    if settings.use_models:
        pipe = _load_pipeline(settings.emotion_model)
        if pipe is not None:
            try:
                out = pipe(text[:1000])
                rows = out[0] if (out and isinstance(out[0], list)) else out
                raw = {str(r["label"]).lower(): float(r["score"]) for r in rows}
                return _normalise({label: raw.get(label, 0.0) for label in EMOTION_LABELS}), "transformer"
            except Exception:
                pass
    return _heuristic(text), "heuristic"


def is_model_loaded() -> bool:
    return _pipeline is not None
