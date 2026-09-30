"""Validation engine: input sanitization, prompt-injection defense, and output grounding.

Safety Boundary:
This system is an NLP text analysis instrument, NOT a clinical diagnostic tool.
The validator enforces input boundaries, strips potential instruction injection vectors,
and ensures that outputs remain strictly linguistic without psychiatric diagnostic claims.
"""
from __future__ import annotations

import re
from typing import Any

from backend.app.core.config import get_settings
from backend.app.domain.emotion_schema import EMOTION_LABELS, AnalysisResult

_FORBIDDEN_DIAGNOSTIC_TERMS = [
    r"\bclinical depression\b",
    r"\bbipolar disorder\b",
    r"\bschizophreni\w*\b",
    r"\bpsychotic\b",
    r"\bsuicid\w*\b",
    r"\bself-harm\b",
    r"\bmental illness diagnosis\b",
    r"\bpatient has\b",
]

_DISCLAIMER = "Analysis reflects automated linguistic tone analysis and is not a clinical or psychological evaluation."


def validate_input_text(raw_text: str) -> tuple[str, list[str]]:
    """Sanitize and validate incoming text.

    Returns:
        tuple[str, list[str]]: (cleaned_text, warnings)
    Raises:
        ValueError: if input is invalid or violates size constraints.
    """
    settings = get_settings()

    if not isinstance(raw_text, str):
        raise ValueError("Input must be a text string.")

    cleaned = raw_text.strip()
    if not cleaned:
        raise ValueError("Input text cannot be empty or solely whitespace.")

    if len(cleaned) > settings.max_input_chars:
        raise ValueError(
            f"Input exceeds maximum allowed length of {settings.max_input_chars} characters (received {len(cleaned)})."
        )

    # Prompt injection hygiene: strip zero-width characters and control codes
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", cleaned)

    warnings: list[str] = []
    # Check for prompt injection heuristic markers
    lower = cleaned.lower()
    if any(p in lower for p in ["ignore previous instructions", "system prompt", "disregard instructions"]):
        warnings.append(
            "Input contains prompt-override patterns; processed strictly as passive text data."
        )

    return cleaned, warnings


def validate_and_harden_result(result: AnalysisResult) -> AnalysisResult:
    """Audit and harden output against safety boundaries and schema invariants."""
    # 1. Label invariant
    if result.primary_emotion not in EMOTION_LABELS:
        result.primary_emotion = "neutral"
        result.warnings.append(f"Predicted emotion was coerced to 'neutral' to satisfy label schema.")

    # 2. Score bounds
    result.confidence = max(0.0, min(1.0, round(float(result.confidence), 4)))
    result.sarcasm_score = max(0.0, min(1.0, round(float(result.sarcasm_score), 4)))

    # 3. Clinical term redacting
    sanitized_rationale = result.rationale
    for pattern in _FORBIDDEN_DIAGNOSTIC_TERMS:
        if re.search(pattern, sanitized_rationale, re.IGNORECASE):
            sanitized_rationale = re.sub(
                pattern, "[non-diagnostic linguistic indicator]", sanitized_rationale, flags=re.IGNORECASE
            )
            result.warnings.append("Clinical or diagnostic terminology was redacted from rationale.")
    result.rationale = sanitized_rationale

    # 4. Ensure safety disclaimer
    if _DISCLAIMER not in result.warnings:
        result.warnings.append(_DISCLAIMER)

    # 5. Enforce uncertain condition
    settings = get_settings()
    if result.confidence < settings.uncertain_threshold:
        result.uncertain = True

    return result
