"""Download pretrained transformer weights for offline/local execution.

Models downloaded:
1. Emotion classifier: j-hartmann/emotion-english-distilroberta-base (~330 MB)
2. Sarcasm detector: helinivan/english-sarcasm-detector (~300 MB)
3. Embedding model: sentence-transformers/all-MiniLM-L6-v2 (~80 MB)

Usage:
    python scripts/download_models.py
"""
from __future__ import annotations

import sys
import time

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer


def download_all():
    print("=" * 65)
    print(" P_098 — Pretrained Transformer Weights Downloader")
    print(" CPU-only & 8GB-RAM friendly (~710 MB total)")
    print("=" * 65)

    models_to_download = [
        ("Emotion Model", "j-hartmann/emotion-english-distilroberta-base", "classifier"),
        ("Sarcasm Model", "helinivan/english-sarcasm-detector", "classifier"),
        ("Embedding Model", "sentence-transformers/all-MiniLM-L6-v2", "embedding"),
    ]

    for label, name, m_type in models_to_download:
        print(f"\n[*] Downloading {label}: '{name}'...")
        t0 = time.time()
        try:
            if m_type == "classifier":
                AutoTokenizer.from_pretrained(name)
                AutoModelForSequenceClassification.from_pretrained(name)
            elif m_type == "embedding":
                SentenceTransformer(name)
            elapsed = time.time() - t0
            print(f"    [+] Successfully cached {label} ({elapsed:.1f}s)")
        except Exception as e:
            print(f"    [!] Warning: Failed to download {label}: {e}")
            print("        Pipeline will gracefully use heuristic fallback when offline.")

    print("\n" + "=" * 65)
    print(" Model download process completed.")
    print("=" * 65)


if __name__ == "__main__":
    download_all()
