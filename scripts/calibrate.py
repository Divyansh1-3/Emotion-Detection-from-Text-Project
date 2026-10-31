"""Fit temperature on GoEmotions dev and validate on disjoint test examples.

Downloads are explicit (--download). Raw text stays in ignored data/raw. The
profile includes only fitted parameters, measurements, source hashes and IDs.
The upstream emotion model used GoEmotions: overlap with its training subset is
unknown, so this is experimental domain calibration, not independent accuracy proof.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SOURCE = "https://raw.githubusercontent.com/google-research/google-research/master/goemotions/data/"
FILES = ["dev.tsv", "test.tsv", "emotions.txt", "ekman_mapping.json"]


def reliability_metrics(probabilities, targets):
    import numpy as np
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(targets, dtype=int)
    correct = p.argmax(axis=1) == y
    confidence = p.max(axis=1)
    ece = 0.0
    bins = []
    for index in range(10):
        mask = (confidence >= index / 10) & (confidence < (index + 1) / 10 if index < 9 else confidence <= 1)
        if mask.any():
            accuracy, mean = float(correct[mask].mean()), float(confidence[mask].mean())
            ece += float(mask.mean()) * abs(accuracy - mean)
            bins.append({"lower": index / 10, "count": int(mask.sum()), "accuracy": accuracy, "mean_confidence": mean})
    return {"n": len(y), "accuracy": float(correct.mean()),
            "nll": float(-np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1)).mean()),
            "brier": float(np.square(p - np.eye(p.shape[1])[y]).sum(axis=1).mean()),
            "ece_10_bins": ece, "bins": bins}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download public calibration data, then exit")
    parser.add_argument("--fit-count", type=int, default=700)
    parser.add_argument("--validation-count", type=int, default=350)
    args = parser.parse_args()
    raw = ROOT / "data/raw/goemotions"
    raw.mkdir(parents=True, exist_ok=True)
    if args.download:
        for filename in FILES:
            with urlopen(SOURCE + filename, timeout=60) as response:
                data = response.read()
            (raw / filename).write_bytes(data)
            print(f"Downloaded {filename}: {len(data)} bytes", flush=True)
        return
    if args.fit_count < 200 or args.validation_count < 100:
        parser.error("Use at least 200 fitting and 100 validation examples")
    if any(not (raw / filename).exists() for filename in FILES):
        parser.error("Run with --download first")

    os.environ.update(USE_MODELS="1", LLM_MODE="mock", CALIBRATION_ENABLED="0")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import numpy as np
    from scipy.optimize import minimize_scalar
    from backend.app.domain.emotion_schema import EMOTION_LABELS
    from backend.app.engines.calibration import configuration_signature, pipeline_fingerprint, temperature_scale
    from backend.app.engines.router import execute_pipeline
    from backend.app.engines.warmup import warm_up_models

    names = (raw / "emotions.txt").read_text().splitlines()
    mapping = json.loads((raw / "ekman_mapping.json").read_text())
    label_map = {fine: coarse for coarse, values in mapping.items() for fine in values}
    label_map["neutral"] = "neutral"
    excluded = set()
    for path in (ROOT / "data/kb").glob("*.jsonl"):
        excluded.update(json.loads(line)["text"].strip().casefold() for line in path.read_text(encoding="utf-8").splitlines() if line)
    for path in (ROOT / "data/eval").glob("*.csv"):
        excluded.update(row["text"].strip().casefold() for row in csv.DictReader(path.open(encoding="utf-8")))
    used_ids, used_texts = set(), set(excluded)
    warm_up_models()

    def collect(filename, count):
        rows = list(csv.reader((raw / filename).open(encoding="utf-8"), delimiter="\t"))
        random.Random(42).shuffle(rows)
        probabilities, targets, ids = [], [], []
        for text, fine_labels, identifier in rows:
            key = text.strip().casefold()
            labels = {label_map[names[int(value)]] for value in fine_labels.split(",")}
            if len(labels) != 1 or identifier in used_ids or key in used_texts:
                continue
            result = execute_pipeline(text)
            if result.language != "en":
                continue
            required = {"emotion_model_transformer", "sarcasm_model_transformer", "retrieval_rag_embeddings"}
            if not required.issubset(result.route):
                raise RuntimeError("Calibration requires all three model paths for every accepted example")
            dist = result.emotion_distribution()
            probabilities.append([dist[label] for label in EMOTION_LABELS])
            targets.append(EMOTION_LABELS.index(next(iter(labels))))
            ids.append(identifier)
            used_ids.add(identifier)
            used_texts.add(key)
            if len(ids) % 100 == 0:
                print(f"{filename}: {len(ids)}/{count}", flush=True)
            if len(ids) == count:
                break
        if len(ids) < count or set(targets) != set(range(len(EMOTION_LABELS))):
            raise RuntimeError("Insufficient disjoint examples or missing emotion classes")
        return np.asarray(probabilities), np.asarray(targets), ids

    fit_p, fit_y, fit_ids = collect("dev.tsv", args.fit_count)
    val_p, val_y, val_ids = collect("test.tsv", args.validation_count)

    def scale_batch(p, temperature):
        logits = np.log(np.clip(p, 1e-12, 1)) / temperature
        logits -= logits.max(axis=1, keepdims=True)
        values = np.exp(logits)
        return values / values.sum(axis=1, keepdims=True)

    def objective(log_temperature):
        return reliability_metrics(scale_batch(fit_p, math.exp(log_temperature)), fit_y)["nll"]

    solution = minimize_scalar(objective, bounds=(math.log(.1), math.log(10)), method="bounded")
    temperature = float(math.exp(solution.x))
    before = reliability_metrics(val_p, val_y)
    after = reliability_metrics(scale_batch(val_p, temperature), val_y)
    passed = bool(solution.success and after["nll"] < before["nll"] and after["brier"] <= before["brier"]
                  and after["ece_10_bins"] <= before["ece_10_bins"])
    profile = {
        "schema_version": 1, "method": "temperature_scaling", "temperature": temperature,
        "validation_passed": passed, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pipeline_fingerprint": pipeline_fingerprint(), "configuration": configuration_signature(),
        "scope": "English, emotion transformer + sarcasm transformer + embedding retrieval",
        "source": SOURCE, "dataset": "GoEmotions, Demszky et al. (2020), official Ekman mapping",
        "source_sha256": {name: hashlib.sha256((raw / name).read_bytes()).hexdigest() for name in FILES},
        "sampling": "seed 42; one mapped label; detected English; exclude KB/evaluation text and duplicates",
        "fit": {"split": "dev", "ids": fit_ids, "class_counts": dict(zip(EMOTION_LABELS, np.bincount(fit_y, minlength=7).tolist())),
                "before": reliability_metrics(fit_p, fit_y), "after": reliability_metrics(scale_batch(fit_p, temperature), fit_y)},
        "validation": {"split": "test", "ids": val_ids, "class_counts": dict(zip(EMOTION_LABELS, np.bincount(val_y, minlength=7).tolist())),
                       "before": before, "after": after},
        "limitations": ["The upstream emotion model used GoEmotions; overlap with its training subset is unknown.",
                        "Domain-specific experimental calibration, not proof of general accuracy or clinical validity.",
                        "Sarcasm scores and Hindi/Hinglish outputs remain uncalibrated."]}
    destination = ROOT / "data/calibration/temperature.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    print(json.dumps({"temperature": temperature, "validation_passed": passed, "before": before, "after": after}), flush=True)
    if not passed:
        raise SystemExit("Validation did not improve all three calibration measures; profile will remain disabled")


if __name__ == "__main__":
    main()
