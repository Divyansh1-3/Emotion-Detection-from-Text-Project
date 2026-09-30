"""Retrieval (RAG) engine — exemplars and knowledge base index.

Provides:
1. Grounding evidence: semantic search over emotion definitions and labelled exemplars
   to provide factual context for the LLM rationale generator.
2. Calibration vote: k-NN classification score distribution derived from retrieved
   exemplar similarities, fused into the final emotion confidence.

Supports sentence-transformers (all-MiniLM-L6-v2) embedding with cosine distance,
with an offline heuristic/TF-IDF fallback so the pipeline works even without models loaded.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional

import numpy as np

from backend.app.core.config import get_settings
from backend.app.domain.emotion_schema import EMOTION_LABELS, RetrievedItem

_lock = threading.Lock()
_model = None
_model_failed = False

_index_cache: dict[str, Any] = {
    "corpus": [],
    "embeddings": None,
    "tfidf_vectorizer": None,
    "tfidf_matrix": None,
    "ready": False,
}


def _get_embedding_model(model_name: str):
    global _model, _model_failed
    if _model is not None or _model_failed:
        return _model
    with _lock:
        if _model is not None or _model_failed:
            return _model
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(model_name)
        except Exception:
            _model_failed = True
            _model = None
    return _model


def load_corpus(kb_dir: Path) -> list[dict[str, Any]]:
    """Load items from emotions.jsonl and exemplars.jsonl."""
    items = []
    emotions_file = kb_dir / "emotions.jsonl"
    exemplars_file = kb_dir / "exemplars.jsonl"

    for file_path in (emotions_file, exemplars_file):
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            items.append(json.loads(line))
                        except Exception:
                            continue
    return items


def initialize_index(force_reload: bool = False) -> bool:
    """Index the KB and exemplar files."""
    settings = get_settings()
    with _lock:
        if _index_cache["ready"] and not force_reload:
            return True

        corpus = load_corpus(settings.kb_dir)
        if not corpus:
            _index_cache["ready"] = True
            return True

        texts = [item["text"] for item in corpus]
        _index_cache["corpus"] = corpus

        # Try dense embeddings if enabled
        if settings.use_models:
            embedder = _get_embedding_model(settings.embedding_model)
            if embedder is not None:
                try:
                    embeddings = embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                    _index_cache["embeddings"] = embeddings
                except Exception:
                    _index_cache["embeddings"] = None

        # Build fallback TF-IDF index
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=1000)
            tfidf_mat = vec.fit_transform(texts)
            _index_cache["tfidf_vectorizer"] = vec
            _index_cache["tfidf_matrix"] = tfidf_mat
        except Exception:
            _index_cache["tfidf_vectorizer"] = None
            _index_cache["tfidf_matrix"] = None

        _index_cache["ready"] = True
        return True


def retrieve_similar(query: str, top_k: int | None = None) -> list[RetrievedItem]:
    """Retrieve top-k most similar exemplars/knowledge snippets for a query."""
    settings = get_settings()
    k = top_k or settings.retrieval_top_k

    if not _index_cache["ready"]:
        initialize_index()

    corpus = _index_cache["corpus"]
    if not corpus:
        return []

    # Dense embedding search
    if _index_cache["embeddings"] is not None and settings.use_models:
        embedder = _get_embedding_model(settings.embedding_model)
        if embedder is not None:
            try:
                q_vec = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
                # Cosine similarity since normalized
                sims = np.dot(_index_cache["embeddings"], q_vec)
                top_indices = np.argsort(sims)[::-1][:k]

                results = []
                for idx in top_indices:
                    item = corpus[idx]
                    results.append(
                        RetrievedItem(
                            text=item["text"],
                            label=item.get("label", "neutral"),
                            similarity=round(float(sims[idx]), 4),
                            source=item.get("source", "exemplar"),
                        )
                    )
                return results
            except Exception:
                pass

    # TF-IDF cosine similarity fallback
    if _index_cache["tfidf_vectorizer"] is not None and _index_cache["tfidf_matrix"] is not None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            vec = _index_cache["tfidf_vectorizer"]
            q_mat = vec.transform([query])
            sims = cosine_similarity(q_mat, _index_cache["tfidf_matrix"])[0]
            top_indices = np.argsort(sims)[::-1][:k]

            results = []
            for idx in top_indices:
                item = corpus[idx]
                results.append(
                    RetrievedItem(
                        text=item["text"],
                        label=item.get("label", "neutral"),
                        similarity=round(float(sims[idx]), 4),
                        source=item.get("source", "exemplar"),
                    )
                )
            return results
        except Exception:
            pass

    # Simple keyword overlap fallback if sklearn is not yet available
    q_words = set(query.lower().split())
    scored = []
    for item in corpus:
        item_words = set(item["text"].lower().split())
        overlap = len(q_words.intersection(item_words)) / max(1, len(q_words.union(item_words)))
        scored.append((overlap, item))
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, item in scored[:k]:
        results.append(
            RetrievedItem(
                text=item["text"],
                label=item.get("label", "neutral"),
                similarity=round(float(score), 4),
                source=item.get("source", "exemplar"),
            )
        )
    return results


def compute_knn_vote(retrieved: list[RetrievedItem]) -> dict[str, float]:
    """Compute a normalized probability distribution over EMOTION_LABELS from retrieved exemplars."""
    vote = {label: 0.0 for label in EMOTION_LABELS}
    total_weight = 0.0

    for item in retrieved:
        if item.source == "exemplar" and item.label in vote:
            weight = max(0.01, item.similarity)
            vote[item.label] += weight
            total_weight += weight

    if total_weight > 0:
        return {k: round(v / total_weight, 4) for k, v in vote.items()}

    # Uniform prior if no exemplars
    uniform = round(1.0 / len(EMOTION_LABELS), 4)
    return {k: uniform for k in EMOTION_LABELS}
