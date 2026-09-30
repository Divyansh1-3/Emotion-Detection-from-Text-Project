"""Bounded LLM engine for grounded emotion & sarcasm explanations.

Key design principles:
1. Purely explanatory: The label and confidence are decided deterministically
   by the fusion engine; the LLM NEVER overrides labels.
2. Grounded & bounded: The prompt supplies only the text, predicted labels, and
   retrieved evidence, forbidding psychiatric diagnosis or speculative claims.
3. Resilient: Works with any OpenAI-compatible provider (OpenAI, Ollama, vLLM, etc.)
   with automatic retry on malformed JSON and instant offline template fallback.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.core.config import get_settings
from backend.app.domain.emotion_schema import EmotionScore, RetrievedItem


def _format_evidence(sources: list[RetrievedItem]) -> str:
    if not sources:
        return "No specific exemplar retrieved."
    lines = []
    for i, s in enumerate(sources[:3], start=1):
        lines.append(f"{i}. [{s.source}:{s.label}] {s.text} (sim: {s.similarity:.2f})")
    return "\n".join(lines)


def _load_prompt_template(prompts_dir: Path) -> str:
    path = prompts_dir / "tasks" / "emotion_rationale_v1.txt"
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            pass
    return (
        "Explain in 1-2 concise sentences why the input text reflects the emotion '{primary_emotion}' "
        "and note sarcasm if detected ({sarcasm}). Input: {input_text}\n"
        "Return valid JSON: {{\"explanation\": \"...\", \"confidence_reason\": \"...\"}}"
    )


def generate_template_rationale(
    input_text: str,
    primary_emotion: str,
    scores: list[EmotionScore],
    sarcasm: bool,
    sarcasm_score: float,
    sources: list[RetrievedItem],
) -> str:
    """Deterministic offline fallback rationale when LLM is offline or disabled."""
    top_score = scores[0].score if scores else 0.5
    cues = []
    if sarcasm:
        cues.append(f"sarcastic tone cues (intensity {sarcasm_score:.2f}) with irony or contrast")
    if top_score >= 0.70:
        cues.append(f"strong alignment with '{primary_emotion}' markers")
    elif top_score >= 0.40:
        cues.append(f"moderate presence of '{primary_emotion}' expressions")
    else:
        cues.append(f"mixed or subtle emotional signals")

    evidence_str = ""
    for s in sources:
        if s.source == "exemplar" and s.similarity > 0.30:
            evidence_str = f" Matches semantic patterns seen in reference exemplars for {primary_emotion}."
            break

    cues_str = ", ".join(cues)
    return (
        f"The text exhibits {cues_str}, reflecting a primary tone of {primary_emotion} "
        f"with {top_score * 100:.1f}% confidence.{evidence_str}"
    )


def generate_rationale(
    input_text: str,
    primary_emotion: str,
    scores: list[EmotionScore],
    sarcasm: bool,
    sarcasm_score: float,
    sources: list[RetrievedItem],
) -> tuple[str, bool]:
    """Generate a grounded 1-2 sentence explanation.

    Returns:
        tuple[str, bool]: (rationale_text, llm_used_boolean)
    """
    settings = get_settings()

    # If LLM disabled or in mock mode, use template fallback directly
    if not settings.llm_enabled:
        return (
            generate_template_rationale(
                input_text, primary_emotion, scores, sarcasm, sarcasm_score, sources
            ),
            False,
        )

    template = _load_prompt_template(settings.prompts_dir)
    top_scores_str = ", ".join([f"{s.label}: {s.score:.2f}" for s in scores[:3]])
    evidence_str = _format_evidence(sources)

    prompt = template.format(
        input_text=input_text,
        primary_emotion=primary_emotion,
        top_scores=top_scores_str,
        sarcasm="Yes" if sarcasm else "No",
        sarcasm_score=f"{sarcasm_score:.2f}",
        retrieved_evidence=evidence_str,
    )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.llm_timeout_seconds,
        )

        for attempt in range(2):
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise, bounded NLP analysis explainer. Output valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.llm_max_tokens,
                temperature=0.2,
                response_format={"type": "json_object"} if attempt == 0 else None,
            )
            raw = response.choices[0].message.content or ""
            try:
                data = json.loads(raw.strip())
                explanation = data.get("explanation", "").strip()
                if explanation:
                    return explanation, True
            except Exception:
                continue

    except Exception:
        pass

    # Fallback if API fails or cannot parse JSON
    return (
        generate_template_rationale(
            input_text, primary_emotion, scores, sarcasm, sarcasm_score, sources
        ),
        False,
    )
