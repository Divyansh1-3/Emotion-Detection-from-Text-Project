"""Run the small project regression set with real models; no training or tuning."""

import csv
import json
import platform
import time
from collections import Counter
from pathlib import Path

from emotion_model import EMOTIONS, EMOTION_MODEL, EMOTION_REVISION, SARCASM_MODEL, SARCASM_REVISION, predict_emotion

ROOT = Path(__file__).resolve().parent


def metrics(expected, predicted, labels):
    f1 = []
    for label in labels:
        tp = sum(a == label and b == label for a, b in zip(expected, predicted))
        fp = sum(a != label and b == label for a, b in zip(expected, predicted))
        fn = sum(a == label and b != label for a, b in zip(expected, predicted))
        f1.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    return {"cases": len(expected), "accuracy": sum(a == b for a, b in zip(expected, predicted)) / len(expected),
            "macro_f1": sum(f1) / len(f1)}


def evaluate():
    import importlib.metadata

    started = time.perf_counter()
    example = predict_emotion("Great, it broke the first day...")
    first_seconds = time.perf_counter() - started
    rows = []
    durations = []
    for task, filename, gold_column in (("emotion", "emotion.csv", "gold_emotion"), ("sarcasm", "sarcasm.csv", "gold_sarcasm")):
        with (ROOT / "data" / "regression" / filename).open(encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                started = time.perf_counter()
                result = predict_emotion(row["text"])
                durations.append((time.perf_counter() - started) * 1000)
                rows.append({"task": task, "text": row["text"], "expected": row[gold_column], "result": result})
    emotion_rows = [row for row in rows if row["task"] == "emotion"]
    sarcasm_rows = [row for row in rows if row["task"] == "sarcasm"]
    raw_sarcasm = ["1" if row["result"]["sarcasm"]["score"] >= 0.5 else "0" for row in sarcasm_rows]
    screenshot_text = "I am busy right now, can I ignore you some other time?"
    screenshot_result = predict_emotion(screenshot_text)
    report = {
        "method": "Two pretrained transformers; CPU float16; no fallback or rule fusion",
        "scope": "Small hand-written project regression set reused from the earlier project. Not an independent benchmark or generalization estimate.",
        "versions": {"python": platform.python_version(), **{p: importlib.metadata.version(p) for p in ("torch", "transformers")}},
        "models": {"emotion": {"id": EMOTION_MODEL, "revision": EMOTION_REVISION}, "sarcasm": {"id": SARCASM_MODEL, "revision": SARCASM_REVISION}},
        "emotion": metrics([r["expected"] for r in emotion_rows], [r["result"]["emotion"] for r in emotion_rows], EMOTIONS),
        "sarcasm_raw_argmax": metrics([r["expected"] for r in sarcasm_rows], raw_sarcasm, ("0", "1")),
        "sarcasm_display_counts": dict(Counter(r["result"]["sarcasm"]["label"] for r in sarcasm_rows)),
        "first_prediction_seconds": first_seconds,
        "warm_mean_ms": sum(durations) / len(durations),
        "warm_p95_ms": sorted(durations)[min(len(durations) - 1, int(len(durations) * 0.95))],
        "timing_scope": "Local Python inference including both models, excluding Streamlit rendering, HTTP and first model download.",
        "sarcastic_example": example,
        "user_reported_sarcastic_example": {"text": screenshot_text, "result": screenshot_result,
            "known_limitation": "The user identifies this as sarcastic; the pretrained irony model may miss its dry humor. This example is reported separately, not used to tune thresholds."},
        "cases": rows,
    }
    path = ROOT / "docs" / "transformer-evaluation.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("cases", "sarcastic_example")}, indent=2))


if __name__ == "__main__":
    evaluate()
