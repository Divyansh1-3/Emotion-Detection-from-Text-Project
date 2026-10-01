"""Unit tests for signal fusion and calibration engine (fusion.py)."""
from __future__ import annotations

from backend.app.domain.emotion_schema import EMOTION_LABELS, decide_uncertain
from backend.app.engines.fusion import fuse_signals
from backend.app.engines.rules import RuleAnalysisResult


def test_fusion_clear_high_confidence():
    # Mock clear joy ML distribution
    ml_dist = {l: 0.05 for l in EMOTION_LABELS}
    ml_dist["joy"] = 0.85
    rule_res = RuleAnalysisResult(
        emotion_hints={l: 0.1 for l in EMOTION_LABELS},
        sarcasm_cue_score=0.1,
    )
    rule_res.emotion_hints["joy"] = 0.8
    knn_dist = {l: 0.1 for l in EMOTION_LABELS}
    knn_dist["joy"] = 0.7

    fused = fuse_signals(
        ml_dist=ml_dist,
        rule_res=rule_res,
        knn_dist=knn_dist,
        sarcasm_ml_prob=0.1,
        ml_backend="transformer",
    )

    assert fused["primary_emotion"] == "joy"
    assert fused["confidence"] > 0.60
    assert fused["uncertain"] is False
    assert fused["sarcasm"] is False


def test_fusion_uncertain_calibration():
    # Close tie between sadness and anger
    ml_dist = {l: 0.10 for l in EMOTION_LABELS}
    ml_dist["sadness"] = 0.28
    ml_dist["anger"] = 0.26
    rule_res = RuleAnalysisResult(
        emotion_hints={l: 0.14 for l in EMOTION_LABELS},
        sarcasm_cue_score=0.2,
    )
    knn_dist = {l: 0.14 for l in EMOTION_LABELS}

    fused = fuse_signals(
        ml_dist=ml_dist,
        rule_res=rule_res,
        knn_dist=knn_dist,
        sarcasm_ml_prob=0.2,
        ml_backend="transformer",
    )

    # Low margin and score should mark as uncertain
    assert fused["uncertain"] is True
    assert any("uncertain" in w.lower() for w in fused["warnings"])


def test_decide_uncertain_logic():
    # High score, high margin -> not uncertain
    assert decide_uncertain(top_score=0.85, margin=0.50, threshold=0.40) is False
    # Low score -> uncertain
    assert decide_uncertain(top_score=0.35, margin=0.15, threshold=0.40) is True
    # Narrow margin -> uncertain
    assert decide_uncertain(top_score=0.60, margin=0.03, threshold=0.40, min_margin=0.10) is True


def test_fusion_pure_joy_suppresses_social_media_irony_bias():
    """Ensure genuine joy is never falsely flipped to sarcasm/anger despite raw model enthusiasm bias."""
    ml_dist = {l: 0.002 for l in EMOTION_LABELS}
    ml_dist["joy"] = 0.98
    rule_res = RuleAnalysisResult(
        emotion_hints=ml_dist,
        sarcasm_cue_score=0.0,
        has_praise_token=False,
        has_adversity_token=False,
    )
    knn_dist = {l: 0.05 for l in EMOTION_LABELS}
    knn_dist["joy"] = 0.70

    fused = fuse_signals(
        ml_dist=ml_dist,
        rule_res=rule_res,
        knn_dist=knn_dist,
        sarcasm_ml_prob=0.82,  # Raw Twitter model gave false-positive 0.82 on enthusiasm
        ml_backend="transformer",
    )

    assert fused["sarcasm"] is False
    assert fused["primary_emotion"] == "joy"


def test_fusion_sarcasm_masks_shifted_to_anger_disgust():
    """Ensure sarcastic praise of an adversity is identified and shifted to anger/disgust."""
    ml_dist = {l: 0.05 for l in EMOTION_LABELS}
    ml_dist["joy"] = 0.75  # Superficial praise
    rule_res = RuleAnalysisResult(
        emotion_hints=ml_dist,
        sarcasm_cue_score=0.50,
        has_praise_token=True,
        has_adversity_token=True,
    )
    knn_dist = {l: 0.05 for l in EMOTION_LABELS}
    knn_dist["anger"] = 0.70

    fused = fuse_signals(
        ml_dist=ml_dist,
        rule_res=rule_res,
        knn_dist=knn_dist,
        sarcasm_ml_prob=0.95,
        ml_backend="transformer",
    )

    assert fused["sarcasm"] is True
    assert fused["primary_emotion"] in ("anger", "disgust")

