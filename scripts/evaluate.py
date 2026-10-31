"""Offline Evaluation Suite for P_098 Emotion Detection.

Evaluates:
1. Emotion Classification: Macro-F1, Weighted-F1, Accuracy, and per-class Precision/Recall/F1
2. Sarcasm Detection: Precision, Recall, F1, and Accuracy
3. Latency benchmarks

Produces:
- docs/evaluation-report.md (detailed Markdown report)
- docs/evaluation-charts.png (per-class F1 performance visualization)

Usage:
    python scripts/evaluate.py
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
from datetime import datetime, timezone
import sys
import time
from pathlib import Path

# Ensure root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_recall_fscore_support,
)

from backend.app.domain.emotion_schema import EMOTION_LABELS
from backend.app.engines.router import execute_pipeline

PATH_COUNTS = {}
CONFIDENCE_COUNTS = {}
REQUIRE_MODELS = False


def measured_pipeline(text):
    result = execute_pipeline(text)
    required = {"emotion_model_transformer", "sarcasm_model_transformer", "retrieval_rag_embeddings"}
    if REQUIRE_MODELS and not required.issubset(result.route):
        raise RuntimeError("Hybrid benchmark encountered a fallback: " + str(result.route))
    for route in result.route:
        if route.startswith(("emotion_model_", "sarcasm_model_", "retrieval_rag_")):
            PATH_COUNTS[route] = PATH_COUNTS.get(route, 0) + 1
    method = result.confidence_method
    CONFIDENCE_COUNTS[method] = CONFIDENCE_COUNTS.get(method, 0) + 1
    return result


def evaluate_emotions(eval_csv_path: Path):
    with open(eval_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    y_true = []
    y_pred = []
    latencies = []

    print(f"[*] Evaluating {len(rows)} emotion test cases...")
    for row in rows:
        text = row["text"]
        gold = row["gold_emotion"].strip().lower()
        t0 = time.perf_counter()
        res = measured_pipeline(text)
        lat = (time.perf_counter() - t0) * 1000.0

        y_true.append(gold)
        y_pred.append(res.primary_emotion)
        latencies.append(lat)

    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    # Per-class metrics
    p, r, f1, s = precision_recall_fscore_support(
        y_true, y_pred, labels=EMOTION_LABELS, zero_division=0
    )

    per_class = {}
    for i, label in enumerate(EMOTION_LABELS):
        per_class[label] = {
            "precision": float(p[i]),
            "recall": float(r[i]),
            "f1": float(f1[i]),
            "support": int(s[i]),
        }

    return {
        "total": len(rows),
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class": per_class,
        "avg_latency_ms": np.mean(latencies),
        "p95_latency_ms": np.percentile(latencies, 95),
        "y_true": y_true,
        "y_pred": y_pred,
    }


def evaluate_sarcasm(eval_csv_path: Path):
    with open(eval_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    y_true = []
    y_pred = []

    print(f"[*] Evaluating {len(rows)} sarcasm test cases...")
    for row in rows:
        text = row["text"]
        gold = int(row["gold_sarcasm"])
        res = measured_pipeline(text)
        pred = 1 if res.sarcasm else 0

        y_true.append(gold)
        y_pred.append(pred)

    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)

    return {
        "total": len(rows),
        "accuracy": acc,
        "precision": p,
        "recall": r,
        "f1": f1,
    }


def generate_charts(emotion_res: dict, sarcasm_res: dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    labels = EMOTION_LABELS
    f1_scores = [emotion_res["per_class"][l]["f1"] * 100 for l in labels]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Emotion F1 bar chart
    colors = ["#dc2626", "#059669", "#9333ea", "#16a34a", "#475569", "#0284c7", "#d97706"]
    bars = ax1.bar(labels, f1_scores, color=colors, edgecolor="#334155")
    ax1.set_title("Per-Emotion F1-Score (%)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("F1 Score (%)")
    ax1.set_ylim(0, 110)
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    ax1.tick_params(axis="x", rotation=30)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # Sarcasm Metrics bar chart
    sarc_metrics = ["Accuracy", "Precision", "Recall", "F1 Score"]
    sarc_values = [
        sarcasm_res["accuracy"] * 100,
        sarcasm_res["precision"] * 100,
        sarcasm_res["recall"] * 100,
        sarcasm_res["f1"] * 100,
    ]
    ax2.bar(sarc_metrics, sarc_values, color="#d946ef", edgecolor="#701a75")
    ax2.set_title("Sarcasm Detection Performance (%)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Metric (%)")
    ax2.set_ylim(0, 110)
    for i, v in enumerate(sarc_values):
        ax2.annotate(f"{v:.1f}%", xy=(i, v), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=9)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"[+] Evaluation chart saved to: {out_path}")


def write_markdown_report(em_res: dict, sarc_res: dict, out_path: Path):
    status = lambda passed: "PASSED" if passed else "FAILED"
    md = f"""# P_098 — Model Evaluation & Performance Report

**Evaluation Date:** {datetime.now(timezone.utc).isoformat()}
**Test Set Size:** {em_res['total']} Emotion Cases, {sarc_res['total']} Sarcasm Cases
**Engine Route:** Hybrid (Preprocess &bull; Rules &bull; Emotion Model &bull; Sarcasm Model &bull; RAG &bull; Fusion)

---

## 1. Executive Summary

| Target Task | Primary Metric | Baseline Target | Measured Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Emotion Classification** | **Macro-F1** | &ge; 0.700 | **{em_res['macro_f1']:.3f}** | **{status(em_res['macro_f1'] >= 0.70)}** |
| **Emotion Classification** | **Accuracy** | &ge; 70.0% | **{em_res['accuracy'] * 100:.1f}%** | **{status(em_res['accuracy'] >= 0.70)}** |
| **Emotion Classification** | **Weighted-F1**| &ge; 0.700 | **{em_res['weighted_f1']:.3f}** | **{status(em_res['weighted_f1'] >= 0.70)}** |
| **Sarcasm Detection** | **F1 Score** | &ge; 0.650 | **{sarc_res['f1']:.3f}** | **{status(sarc_res['f1'] >= 0.65)}** |
| **Inference Latency** | **Mean Latency** | < 150 ms (CPU) | **{em_res['avg_latency_ms']:.1f} ms** | **{status(em_res['avg_latency_ms'] < 150)}** |

---

## 2. Per-Class Emotion Breakdown

| Emotion Label | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
"""
    for l, m in em_res["per_class"].items():
        md += f"| **{l.capitalize()}** | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['support']} |\n"

    md += f"""
**Macro Average:** Precision: {np.mean([m['precision'] for m in em_res['per_class'].values()]):.3f} &bull; Recall: {np.mean([m['recall'] for m in em_res['per_class'].values()]):.3f} &bull; **F1: {em_res['macro_f1']:.3f}**

---

## 3. Sarcasm Detection Metrics

- **Accuracy:** {sarc_res['accuracy'] * 100:.1f}%
- **Precision:** {sarc_res['precision']:.3f}
- **Recall:** {sarc_res['recall']:.3f}
- **F1 Score:** {sarc_res['f1']:.3f}

*Sarcasm policy:* Detected irony is flagged and can redistribute emotion scores toward anger/disgust. This is a heuristic and may be wrong.

---

## 4. Latency Benchmarks (CPU Inference)

- **Mean Pipeline Latency:** `{em_res['avg_latency_ms']:.1f} ms`
- **95th Percentile Latency:** `{em_res['p95_latency_ms']:.1f} ms`

Latency measures the warm pipeline including template rationale, excluding startup, HTTP and persistence. Memory usage is not measured by this script. This small curated sample does not establish general accuracy.

---

## 5. Visual Performance Charts

![Evaluation Performance Charts](evaluation-charts.png)
"""
    out_path.write_text(md, encoding="utf-8")
    print(f"[+] Evaluation markdown report written to: {out_path}")


def main():
    global REQUIRE_MODELS
    parser = argparse.ArgumentParser(description="Reproducible local evaluation; never calls an LLM API.")
    parser.add_argument("--mode", choices=["hybrid", "fallback"], default="hybrid")
    parser.add_argument("--check", action="store_true", help="Exit unsuccessfully if any target is missed")
    args = parser.parse_args()
    REQUIRE_MODELS = args.mode == "hybrid"
    os.environ["LLM_MODE"] = "mock"
    os.environ["USE_MODELS"] = "1" if args.mode == "hybrid" else "0"
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from backend.app.engines.warmup import warm_up_models
    from backend.app.engines.emotion_model import is_model_loaded
    from backend.app.engines.sarcasm_model import is_model_loaded as sarcasm_loaded
    from backend.app.engines.retrieval import retrieve_similar, retrieval_backend
    from backend.app.engines.calibration import calibration_profile
    from backend.app.core.config import get_settings
    started = time.perf_counter()
    warm_up_models()
    retrieve_similar("Warm up retrieval")
    startup_ms = (time.perf_counter() - started) * 1000
    if args.mode == "hybrid" and not (is_model_loaded() and sarcasm_loaded() and retrieval_backend() == "embeddings"):
        raise SystemExit("Hybrid evaluation requires all three model paths. Download models first, or select --mode fallback.")
    em = evaluate_emotions(ROOT / "data/eval/emotion_eval.csv")
    sarc = evaluate_sarcasm(ROOT / "data/eval/sarcasm_eval.csv")
    suffix = "" if args.mode == "hybrid" else "-fallback"
    target = ROOT / "docs" / ("evaluation-report" + suffix + ".md")
    target.parent.mkdir(exist_ok=True)
    write_markdown_report(em, sarc, target)
    chart = "evaluation-charts" + suffix + ".png"
    generate_charts(em, sarc, target.parent / chart)
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "mode": args.mode,
        "retrieval": retrieval_backend(), "llm": "mock", "python": platform.python_version(),
        "platform": platform.platform(), "cpu": platform.processor(),
        "torch_threads": os.getenv("TORCH_NUM_THREADS", "2"), "startup_ms": startup_ms,
        "parallel_inference": get_settings().parallel_inference,
        "calibration_status": calibration_profile()[1],
        "actual_path_counts": PATH_COUNTS, "confidence_method_counts": CONFIDENCE_COUNTS,
        "emotion": em, "sarcasm": sarc,
    }
    (target.parent / ("evaluation-results" + suffix + ".json")).write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    text = target.read_text(encoding="utf-8").replace("evaluation-charts.png", chart)
    text = text.replace("**Engine Route:** Hybrid (Preprocess &bull; Rules &bull; Emotion Model &bull; Sarcasm Model &bull; RAG &bull; Fusion)",
                        f"**Mode:** {args.mode}; retrieval={retrieval_backend()}; LLM=mock; Python={platform.python_version()}\n**Startup:** {startup_ms:.1f} ms (reported separately from warm latency)")
    target.write_text(text, encoding="utf-8")
    with target.open("a", encoding="utf-8") as report:
        report.write("\n## Run verification\n\nEvery hybrid case must use both transformers and embedding retrieval, or the evaluator aborts.\n\n")
        report.write(f"Parallel inference: {metadata['parallel_inference']}. Calibration profile: {metadata['calibration_status']}.\n\n")
        report.write(f"Actual backend counts: `{PATH_COUNTS}`. Confidence methods: `{CONFIDENCE_COUNTS}`.\n")
    print(json.dumps({"mode": args.mode, "emotion_f1": em["macro_f1"], "sarcasm_f1": sarc["f1"], "warm_mean_ms": em["avg_latency_ms"], "startup_ms": startup_ms}))
    if args.check and not (em["macro_f1"] >= .70 and em["accuracy"] >= .70 and sarc["f1"] >= .65 and em["avg_latency_ms"] < 150):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
