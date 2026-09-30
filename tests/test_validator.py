"""Unit tests for validation and safety engine (validator.py)."""
from __future__ import annotations

import pytest

from backend.app.domain.emotion_schema import AnalysisResult, EmotionScore
from backend.app.engines.validator import validate_and_harden_result, validate_input_text


def test_validator_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_input_text("   ")


def test_validator_rejects_oversized():
    huge_text = "word " * 1200
    with pytest.raises(ValueError, match="exceeds maximum"):
        validate_input_text(huge_text)


def test_validator_strips_control_characters():
    dirty_text = "Hello\x00\x08 world\x1F!"
    clean, _ = validate_input_text(dirty_text)
    assert clean == "Hello world!"


def test_validator_redacts_diagnostic_claims():
    res = AnalysisResult(
        input_text="I am sad today.",
        primary_emotion="sadness",
        emotion_scores=[EmotionScore(label="sadness", score=0.85)],
        confidence=0.85,
        uncertain=False,
        sarcasm=False,
        sarcasm_score=0.05,
        rationale="The patient has clinical depression based on severe apathy.",
    )
    hardened = validate_and_harden_result(res)
    assert "clinical depression" not in hardened.rationale
    assert "[non-diagnostic linguistic indicator]" in hardened.rationale
    assert any("redacted" in w.lower() for w in hardened.warnings)


def test_validator_enforces_safety_disclaimer():
    res = AnalysisResult(
        input_text="Just normal text",
        primary_emotion="neutral",
        emotion_scores=[EmotionScore(label="neutral", score=0.9)],
        confidence=0.9,
        uncertain=False,
        sarcasm=False,
        sarcasm_score=0.0,
        rationale="Clean rationale.",
    )
    hardened = validate_and_harden_result(res)
    assert any("automated linguistic tone analysis" in w for w in hardened.warnings)
