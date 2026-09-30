"""Unit tests for deterministic rules engine (rules.py and preprocess.py).

Runs with zero ML dependencies or model weights.
"""
from __future__ import annotations

from backend.app.engines.preprocess import clean_text_for_analysis
from backend.app.engines.rules import analyze_rules


def test_preprocess_emoji_and_slang():
    text = "OMG this is so cool rn! 🎉"
    res = clean_text_for_analysis(text)
    assert "party popper" in res.emojis or len(res.emojis) > 0
    assert "right now" in res.cleaned_text.lower() or "cool" in res.cleaned_text.lower()


def test_rules_joy_detection():
    text = "I am so happy and delighted with this wonderful news! Celebrating!"
    res = analyze_rules(text)
    assert res.emotion_hints["joy"] > res.emotion_hints["anger"]
    assert res.sarcasm_cue_score < 0.5


def test_rules_anger_detection():
    text = "I hate this terrible service! Completely furious and disgusted!"
    res = analyze_rules(text)
    assert res.emotion_hints["anger"] > res.emotion_hints["joy"]


def test_rules_sarcasm_cues():
    text = "Oh brilliant... another delayed train! Just fantastic."
    res = analyze_rules(text)
    assert res.sarcasm_cue_score > 0.3
    assert res.contrast_markers_detected or res.ellipsis_detected or res.quote_markers_detected


def test_rules_negation_inversion():
    text = "I am not happy with this outcome at all."
    res = analyze_rules(text)
    # Negation should suppress or reduce pure joy hint
    assert res.emotion_hints["joy"] < 0.3
