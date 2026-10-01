"""Model pre-warming utility for P_098 Emotion Detection.

Loads HuggingFace transformer models and dense sentence embedding indices into RAM
at server boot time, eliminating the 30-40 second first-request cold start penalty.
"""
from __future__ import annotations

import os
import sys

# Ensure Hugging Face avoids unauthenticated network pings to huggingface.co
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from backend.app.core.config import get_settings


def warm_up_models() -> None:
    """Pre-warm transformer pipelines and embedding index into RAM."""
    settings = get_settings()
    if not settings.use_models:
        print("[*] Models disabled in settings (USE_MODELS=0). Running in fast heuristic mode.")
        return

    print("[*] Pre-warming transformer models into RAM (one-time startup)...")
    sys.stdout.flush()

    try:
        from backend.app.engines.emotion_model import predict_emotions
        from backend.app.engines.sarcasm_model import predict_sarcasm
        from backend.app.engines.retrieval import initialize_index

        # Pre-warm emotion classification model
        print("  -> Loading DistilRoBERTa emotion classifier...")
        sys.stdout.flush()
        predict_emotions("Warm up emotion model")

        # Pre-warm sarcasm classification model
        print("  -> Loading RoBERTa sarcasm detector...")
        sys.stdout.flush()
        predict_sarcasm("Warm up sarcasm model")

        # Pre-warm dense embedding index
        print("  -> Initializing SentenceTransformer knowledge base index...")
        sys.stdout.flush()
        initialize_index()

        print("[+] All neural models successfully loaded and ready for instant inference!")
        sys.stdout.flush()
    except Exception as e:
        print(f"[!] Warning during model warm-up: {e}")
        print("    Pipeline will gracefully fall back to local heuristics if needed.")
        sys.stdout.flush()
