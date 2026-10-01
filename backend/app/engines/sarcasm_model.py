"""Sarcasm ML engine — pretrained transformer with a rule-cue fallback.

Returns a sarcasm probability in [0, 1].  Different community sarcasm models
use different label names, so we map the common variants; whatever the model
says is later *blended with the deterministic rule cues* in fusion, and the
result is always surfaced as an approximate flag (never used to silently flip
the predicted emotion).
"""
from __future__ import annotations

import threading

from backend.app.core.config import get_settings
from backend.app.engines.rules import analyze_rules

_lock = threading.Lock()
_pipeline = None
_load_failed = False

_SARCASTIC_LABELS = {"label_1", "sarcasm", "sarcastic", "irony", "ironic", "1", "yes"}


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
                _pipeline = pipeline("text-classification", model=model_name, model_kwargs={"local_files_only": True})
            except Exception:
                _pipeline = pipeline("text-classification", model=model_name)
        except Exception:
            _load_failed = True
            _pipeline = None
    return _pipeline


def predict_sarcasm(text: str) -> tuple[float, str]:
    """Return (sarcasm_probability, backend: 'transformer'|'heuristic')."""
    settings = get_settings()
    rule_score = round(analyze_rules(text).sarcasm_cue_score, 4)
    if settings.use_models:
        pipe = _load_pipeline(settings.sarcasm_model)
        if pipe is not None:
            try:
                out = pipe(text[:512])
                row = out[0] if isinstance(out, list) else out
                label = str(row["label"]).lower()
                score = float(row["score"])
                ml_prob = score if label in _SARCASTIC_LABELS else (1.0 - score)
                return round(max(0.0, min(1.0, ml_prob)), 4), "transformer"
            except Exception:
                pass
    return rule_score, "heuristic"


def is_model_loaded() -> bool:
    return _pipeline is not None
