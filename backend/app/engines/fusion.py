"""Fusion and calibration engine.

Combines signals from:
1. Transformer emotion probability distribution (or heuristic fallback)
2. Deterministic rule cues (lexicon hints, negations, emojis)
3. RAG k-NN exemplar vote

Then calculates:
- Calibrated confidence and margin
- 'Uncertain' badge determination (top score < threshold or top-2 margin < 0.10)
- Sarcasm flag (blended from ML sarcasm classifier and rule cues)
"""
from __future__ import annotations

from typing import Any

from backend.app.core.config import get_settings
from backend.app.domain.emotion_schema import (
    EMOTION_LABELS,
    EmotionScore,
    decide_uncertain,
    sorted_scores,
)
from backend.app.engines.rules import RuleAnalysisResult


def fuse_signals(
    ml_dist: dict[str, float],
    rule_res: RuleAnalysisResult,
    knn_dist: dict[str, float],
    sarcasm_ml_prob: float,
    ml_backend: str = "transformer",
) -> dict[str, Any]:
    """Fuse probabilistic, rule-based, and retrieval signals into calibrated predictions."""
    settings = get_settings()

    # Determine weighting weights based on whether a true transformer model ran
    has_rule_signal = any(v > 0 for v in rule_res.emotion_hints.values())
    if ml_backend == "transformer":
        w_ml = 0.70
        w_rule = 0.15
        w_knn = 0.15
    else:
        if has_rule_signal:
            w_ml = 0.0
            w_rule = 0.75
            w_knn = 0.25
        else:
            # If no rule cues matched, use neutral heuristic distribution as baseline
            w_ml = 0.60
            w_rule = 0.0
            w_knn = 0.40

    blended: dict[str, float] = {}
    for label in EMOTION_LABELS:
        p_ml = ml_dist.get(label, 0.0)
        p_rule = rule_res.emotion_hints.get(label, 0.0)
        p_knn = knn_dist.get(label, 0.0)

        score = (w_ml * p_ml) + (w_rule * p_rule) + (w_knn * p_knn)
        blended[label] = score

    # Sarcasm signal fusion
    if ml_backend == "transformer":
        if rule_res.sarcasm_cue_score >= 0.40:
            sarcasm_prob = round(max(rule_res.sarcasm_cue_score, 0.40 * sarcasm_ml_prob + 0.60 * rule_res.sarcasm_cue_score), 4)
        else:
            sarcasm_prob = round(max(sarcasm_ml_prob, 0.75 * sarcasm_ml_prob + 0.25 * rule_res.sarcasm_cue_score), 4)
    else:
        sarcasm_prob = round(rule_res.sarcasm_cue_score, 4)

    is_sarcastic = sarcasm_prob >= settings.sarcasm_threshold

    # EMOTION CORRECTION FOR SARCASM
    # Sarcasm uses positive/ironic words (Joy/Surprise) or deadpan delivery (Neutral) to mask Anger or Disgust.
    # When sarcasm is detected, discount false superficial "joy"/"surprise"/"neutral" and elevate anger/disgust.
    if is_sarcastic:
        shift_amount = 0.0
        if blended.get("joy", 0.0) > 0.15:
            joy_pen = blended["joy"] * min(sarcasm_prob, 0.90)
            blended["joy"] -= joy_pen
            shift_amount += joy_pen
        if blended.get("surprise", 0.0) > 0.20 and (rule_res.sarcasm_cue_score >= 0.40 or rule_res.contrast_markers_detected):
            surp_pen = blended["surprise"] * 0.70 * sarcasm_prob
            blended["surprise"] -= surp_pen
            shift_amount += surp_pen
        if blended.get("neutral", 0.0) > 0.35:
            neut_pen = blended["neutral"] * min(sarcasm_prob, 0.75)
            blended["neutral"] -= neut_pen
            shift_amount += neut_pen

        if shift_amount > 0:
            blended["anger"] = blended.get("anger", 0.0) + (shift_amount * 0.70)
            blended["disgust"] = blended.get("disgust", 0.0) + (shift_amount * 0.30)

    total = sum(blended.values())
    if total > 0:
        normalized = {k: round(v / total, 4) for k, v in blended.items()}
    else:
        uniform = round(1.0 / len(EMOTION_LABELS), 4)
        normalized = {k: uniform for k in EMOTION_LABELS}

    ordered = sorted_scores(normalized)
    top_label = ordered[0].label
    top_score = ordered[0].score
    second_score = ordered[1].score if len(ordered) > 1 else 0.0
    margin = round(top_score - second_score, 4)

    # Uncertainty decision
    uncertain = decide_uncertain(
        top_score=top_score,
        margin=margin,
        threshold=settings.uncertain_threshold,
        min_margin=0.10,
    )

    warnings = []
    if uncertain:
        warnings.append(
            f"Classification confidence is low (score: {top_score:.2f}, margin: {margin:.2f}). Marked as uncertain."
        )
    if is_sarcastic:
        warnings.append(
            f"Sarcasm cues detected (score: {sarcasm_prob:.2f}). Tone may be ironic or opposite of literal words."
        )

    return {
        "primary_emotion": top_label,
        "emotion_scores": ordered,
        "confidence": top_score,
        "margin": margin,
        "uncertain": uncertain,
        "sarcasm": is_sarcastic,
        "sarcasm_score": sarcasm_prob,
        "warnings": warnings,
    }
