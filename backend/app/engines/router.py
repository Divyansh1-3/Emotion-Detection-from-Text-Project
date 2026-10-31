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
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from backend.app.domain.emotion_schema import AnalysisResult
from backend.app.core.config import get_settings
from backend.app.engines.emotion_model import predict_emotions
from backend.app.engines.fusion import fuse_signals
from backend.app.engines.llm import generate_rationale
from backend.app.engines.preprocess import preprocess
from backend.app.engines.retrieval import compute_knn_vote, retrieve_with_backend
from backend.app.engines.rules import analyze_rules
from backend.app.engines.sarcasm_model import predict_sarcasm
from backend.app.engines.validator import validate_and_harden_result, validate_input_text

_inference_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="emotion-inference")


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
    prep = preprocess(cleaned_text)
    if prep.language_adapted:
        route.append("hindi_hinglish_phrase_normalization")
        engines_used.append("Hindi/Hinglish phrase normalization")
        warnings.append("Common Hindi/Hinglish phrases were normalized for English models; this is limited phrase support, not general translation. Review the prediction.")

    # 3. Deterministic Rules
    route.append("rules")
    engines_used.append("rules")
    rule_res = analyze_rules(prep.cleaned, pre=prep)

    # Independent inference stages share a bounded pool; the route lists logical stages.
    settings = get_settings()
    if settings.use_models and settings.parallel_inference:
        emotion_future = _inference_pool.submit(predict_emotions, prep.cleaned, rule_res)
        sarcasm_future = _inference_pool.submit(predict_sarcasm, prep.cleaned, rule_res)
        retrieval_future = _inference_pool.submit(retrieve_with_backend, prep.cleaned)
        ml_dist, ml_backend = emotion_future.result()
        sarcasm_ml_prob, sarcasm_backend = sarcasm_future.result()
        retrieved, actual_retrieval = retrieval_future.result()
    else:
        ml_dist, ml_backend = predict_emotions(prep.cleaned, rule_res)
        sarcasm_ml_prob, sarcasm_backend = predict_sarcasm(prep.cleaned, rule_res)
        retrieved, actual_retrieval = retrieve_with_backend(prep.cleaned)

    # 4. Emotion ML Model
    route.append(f"emotion_model_{ml_backend}")
    engines_used.append(f"emotion_model ({ml_backend})")

    # 5. Sarcasm ML Model
    route.append(f"sarcasm_model_{sarcasm_backend}")
    engines_used.append(f"sarcasm_model ({sarcasm_backend})")

    # 6. Semantic Retrieval (RAG) & k-NN vote
    route.append(f"retrieval_rag_{actual_retrieval}")
    engines_used.append(f"retrieval_rag ({actual_retrieval})")
    if actual_retrieval != "embeddings":
        warnings.append(f"Semantic retrieval unavailable or disabled; used {actual_retrieval} retrieval.")
    if sarcasm_backend != "transformer":
        warnings.append("Sarcasm model unavailable or disabled; using approximate rule cues.")
    if prep.language != "en":
        warnings.append("Models are optimized for English; language detection is approximate and other languages may be unreliable.")
    if len(prep.cleaned) > 1000:
        warnings.append("Transformer inputs are limited to 512 tokens; long text may be truncated by the tokenizer.")
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
        calibration_eligible=(prep.language == "en" and ml_backend == "transformer"
                              and sarcasm_backend == "transformer" and actual_retrieval == "embeddings"),
    )
    warnings.extend(fused["warnings"])
    if prep.language != "en":
        fused["uncertain"] = True
    route.append("confidence_" + fused["confidence_method"])

    # 8. Bounded Explanation (LLM / Template Fallback)
    rationale, llm_used = generate_rationale(
        input_text=prep.cleaned,
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
        language=prep.language,
        sources=retrieved,
        warnings=warnings,
        engines_used=engines_used,
        route=route,
        llm_used=llm_used,
        latency_ms=latency_ms,
        request_id=request_id,
        session_id=session_id or "",
        mode=mode,
        confidence_method=fused["confidence_method"],
    )

    return validate_and_harden_result(result)
