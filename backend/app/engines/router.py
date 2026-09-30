"""Hybrid Router — orchestrates the 6 engines and records the execution trace.

Coordinates:
- Input validation (validator.py)
- Preprocessing (preprocess.py)
- Deterministic rules (rules.py)
- Emotion transformer / fallback (emotion_model.py)
- Sarcasm classifier / fallback (sarcasm_model.py)
- Semantic RAG retrieval & k-NN vote (retrieval.py)
- Signal fusion & uncertainty calibration (fusion.py)
- Bounded explanation (llm.py)
- Safety & schema validation (validator.py)
"""
from __future__ import annotations

import time
import uuid
from typing import Any

from backend.app.domain.emotion_schema import AnalysisResult
from backend.app.engines.emotion_model import predict_emotions
from backend.app.engines.fusion import fuse_signals
from backend.app.engines.llm import generate_rationale
from backend.app.engines.preprocess import clean_text_for_analysis
from backend.app.engines.retrieval import compute_knn_vote, retrieve_similar
from backend.app.engines.rules import analyze_rules
from backend.app.engines.sarcasm_model import predict_sarcasm
from backend.app.engines.validator import validate_and_harden_result, validate_input_text


def execute_pipeline(
    raw_text: str,
    session_id: str = "",
    mode: str = "single",
    options: dict[str, Any] | None = None,
) -> AnalysisResult:
    """Run an end-to-end emotion analysis request through the hybrid engines."""
    t0 = time.perf_counter()
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    route: list[str] = []
    engines_used: list[str] = []
    warnings: list[str] = []

    # 1. Input Validation
    route.append("input_validation")
    engines_used.append("validator")
    cleaned_text, input_warns = validate_input_text(raw_text)
    warnings.extend(input_warns)

    # 2. Preprocess & Language
    route.append("preprocess")
    engines_used.append("preprocess")
    prep = clean_text_for_analysis(cleaned_text)

    # 3. Deterministic Rules
    route.append("rules")
    engines_used.append("rules")
    rule_res = analyze_rules(prep.cleaned_text)

    # 4. Emotion ML Model
    ml_dist, ml_backend = predict_emotions(prep.cleaned_text)
    route.append(f"emotion_model_{ml_backend}")
    engines_used.append(f"emotion_model ({ml_backend})")

    # 5. Sarcasm ML Model
    sarcasm_ml_prob, sarcasm_backend = predict_sarcasm(prep.cleaned_text)
    route.append(f"sarcasm_model_{sarcasm_backend}")
    engines_used.append(f"sarcasm_model ({sarcasm_backend})")

    # 6. Semantic Retrieval (RAG) & k-NN vote
    route.append("retrieval_rag")
    engines_used.append("retrieval_rag")
    retrieved = retrieve_similar(prep.cleaned_text)
    knn_vote = compute_knn_vote(retrieved)

    # 7. Signal Fusion & Calibration
    route.append("fusion_calibration")
    engines_used.append("fusion")
    fused = fuse_signals(
        ml_dist=ml_dist,
        rule_res=rule_res,
        knn_dist=knn_vote,
        sarcasm_ml_prob=sarcasm_ml_prob,
        ml_backend=ml_backend,
    )
    warnings.extend(fused["warnings"])

    # 8. Bounded Explanation (LLM / Template Fallback)
    rationale, llm_used = generate_rationale(
        input_text=prep.cleaned_text,
        primary_emotion=fused["primary_emotion"],
        scores=fused["emotion_scores"],
        sarcasm=fused["sarcasm"],
        sarcasm_score=fused["sarcasm_score"],
        sources=retrieved,
    )
    route.append(f"rationale_{'llm' if llm_used else 'template_fallback'}")
    engines_used.append(f"rationale ({'llm' if llm_used else 'template_fallback'})")

    # 9. Assembly & Output Hardening
    route.append("output_validation")
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    result = AnalysisResult(
        input_text=cleaned_text,
        primary_emotion=fused["primary_emotion"],
        emotion_scores=fused["emotion_scores"],
        confidence=fused["confidence"],
        uncertain=fused["uncertain"],
        sarcasm=fused["sarcasm"],
        sarcasm_score=fused["sarcasm_score"],
        rationale=rationale,
        language=prep.detected_language,
        sources=retrieved,
        warnings=warnings,
        engines_used=engines_used,
        route=route,
        llm_used=llm_used,
        latency_ms=latency_ms,
        request_id=request_id,
        session_id=session_id or "",
        mode=mode,
    )

    return validate_and_harden_result(result)
