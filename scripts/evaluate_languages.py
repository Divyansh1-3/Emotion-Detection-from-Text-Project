"""Demonstration coverage of supported Hindi/Hinglish phrases, not a language benchmark."""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    os.environ.update(USE_MODELS="1", LLM_MODE="mock")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from backend.app.engines.router import execute_pipeline
    from backend.app.engines.warmup import warm_up_models
    warm_up_models()
    rows = list(csv.DictReader((ROOT / "data/eval/language_eval.csv").open(encoding="utf-8")))
    results = []
    for row in rows:
        result = execute_pipeline(row["text"])
        required = {"emotion_model_transformer", "sarcasm_model_transformer", "retrieval_rag_embeddings"}
        if not required.issubset(result.route):
            raise RuntimeError("Language evaluation encountered a model fallback")
        results.append({**row, "predicted": result.primary_emotion, "detected_language": result.language,
                        "uncertain": result.uncertain, "confidence_method": result.confidence_method,
                        "correct": result.primary_emotion == row["gold_emotion"]})
    summary = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "total": len(results),
               "correct": sum(row["correct"] for row in results), "results": results,
               "limitations": "Curated examples of supported phrases, not independent multilingual accuracy. No Hindi/Hinglish sarcasm benchmark. All adapted outputs require review."}
    (ROOT / "docs/language-evaluation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Hindi and Hinglish demonstration coverage", "", summary["limitations"], "",
             f"Result: {summary['correct']}/{summary['total']} expected emotion labels; both transformers and embeddings verified for every case.", "",
             "| Input | Expected | Predicted | Requires review |", "|---|---|---|---|"]
    lines.extend(f"| {row['text']} | {row['gold_emotion']} | {row['predicted']} | {row['uncertain']} |" for row in results)
    (ROOT / "docs/language-evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}))
    if not all(row["uncertain"] and row["confidence_method"] == "uncalibrated_fusion" for row in results):
        raise SystemExit("Language uncertainty/calibration policy failed")


if __name__ == "__main__":
    main()
