"""Domain model for emotion analysis.

These are plain value objects shared across every engine and the persistence
layer.  Keeping them free of framework code makes the pipeline easy to unit
test without Flask, a database or any model weights.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

# The 6–8 label MVP target.  These match the output labels of the default
# emotion transformer (j-hartmann/emotion-english-distilroberta-base).
EMOTION_LABELS: list[str] = [
    "anger",
    "disgust",
    "fear",
    "joy",
    "neutral",
    "sadness",
    "surprise",
]

EMOTION_EMOJI: dict[str, str] = {
    "anger": "\U0001F620",
    "disgust": "\U0001F922",
    "fear": "\U0001F628",
    "joy": "\U0001F604",
    "neutral": "\U0001F610",
    "sadness": "\U0001F622",
    "surprise": "\U0001F62E",
}


@dataclass
class EmotionScore:
    """A single emotion label and its (0..1) probability."""

    label: str
    score: float


@dataclass
class RetrievedItem:
    """One retrieved RAG exemplar / knowledge snippet used for grounding."""

    text: str
    label: str
    similarity: float
    source: str = "exemplar"          # "exemplar" | "knowledge"


@dataclass
class AnalysisResult:
    """The single source of truth returned by the pipeline and persisted.

    The frontend renders exactly this object; the ``/inspect`` backend view and
    the ``/results`` API read it back from the database — so the two never
    diverge and nothing is computed client-side.
    """

    input_text: str
    primary_emotion: str
    emotion_scores: list[EmotionScore]
    confidence: float
    uncertain: bool
    sarcasm: bool
    sarcasm_score: float
    rationale: str
    language: str = "en"
    sources: list[RetrievedItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    engines_used: list[str] = field(default_factory=list)
    route: list[str] = field(default_factory=list)
    llm_used: bool = False
    latency_ms: float = 0.0
    request_id: str = ""
    session_id: str = ""
    mode: str = "single"              # "single" | "batch"
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def emotion_distribution(self) -> dict[str, float]:
        return {e.label: e.score for e in self.emotion_scores}


def sorted_scores(distribution: dict[str, float]) -> list[EmotionScore]:
    """Turn a {label: score} mapping into a descending EmotionScore list."""
    return [
        EmotionScore(label=k, score=round(float(v), 4))
        for k, v in sorted(distribution.items(), key=lambda kv: kv[1], reverse=True)
    ]


def decide_uncertain(top_score: float, margin: float, threshold: float, min_margin: float = 0.10) -> bool:
    """Result is 'uncertain' when the top score is low OR the top two are close."""
    return top_score < threshold or margin < min_margin
