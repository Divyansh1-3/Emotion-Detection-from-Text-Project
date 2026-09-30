"""Pre-build and verify the RAG semantic retrieval index.

Builds embeddings from data/kb/emotions.jsonl and data/kb/exemplars.jsonl
and verifies that nearest-neighbor search functions accurately.

Usage:
    python scripts/build_index.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.engines.retrieval import initialize_index, retrieve_similar


def main():
    print("=" * 65)
    print(" P_098 — Building RAG Knowledge Base and Exemplar Index")
    print("=" * 65)

    t0 = time.time()
    ok = initialize_index(force_reload=True)
    elapsed = time.time() - t0

    if not ok:
        print("[!] Index initialization encountered an error.")
        sys.exit(1)

    print(f"[+] Index initialized in {elapsed:.2f}s")

    # Run verification test queries
    test_queries = [
        "I just got accepted into the fellowship! So happy!",
        "This flight delay is completely unacceptable and ridiculous.",
        "A strange scraping noise in the pitch black hallway.",
    ]

    print("\n[*] Running test retrievals:")
    for q in test_queries:
        print(f"\nQuery: \"{q}\"")
        results = retrieve_similar(q, top_k=2)
        for r in results:
            print(f"  -> [{r.source}:{r.label}] {r.text[:65]}... (sim: {r.similarity:.3f})")

    print("\n" + "=" * 65)
    print(" RAG retrieval index ready.")
    print("=" * 65)


if __name__ == "__main__":
    main()
