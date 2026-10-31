# P_098 — Model Evaluation & Performance Report

**Evaluation Date:** 2026-10-31T19:34:05.706750+00:00
**Test Set Size:** 35 Emotion Cases, 35 Sarcasm Cases
**Mode:** hybrid; retrieval=embeddings; LLM=mock; Python=3.11.9
**Startup:** 16130.4 ms (reported separately from warm latency)

---

## 1. Executive Summary

| Target Task | Primary Metric | Baseline Target | Measured Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Emotion Classification** | **Macro-F1** | &ge; 0.700 | **0.913** | **PASSED** |
| **Emotion Classification** | **Accuracy** | &ge; 70.0% | **91.4%** | **PASSED** |
| **Emotion Classification** | **Weighted-F1**| &ge; 0.700 | **0.913** | **PASSED** |
| **Sarcasm Detection** | **F1 Score** | &ge; 0.650 | **0.842** | **PASSED** |
| **Inference Latency** | **Mean Latency** | < 150 ms (CPU) | **139.2 ms** | **PASSED** |

---

## 2. Per-Class Emotion Breakdown

| Emotion Label | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **Anger** | 0.750 | 0.600 | 0.667 | 5 |
| **Disgust** | 0.714 | 1.000 | 0.833 | 5 |
| **Fear** | 1.000 | 1.000 | 1.000 | 5 |
| **Joy** | 1.000 | 1.000 | 1.000 | 5 |
| **Neutral** | 1.000 | 1.000 | 1.000 | 5 |
| **Sadness** | 1.000 | 0.800 | 0.889 | 5 |
| **Surprise** | 1.000 | 1.000 | 1.000 | 5 |

**Macro Average:** Precision: 0.923 &bull; Recall: 0.914 &bull; **F1: 0.913**

---

## 3. Sarcasm Detection Metrics

- **Accuracy:** 82.9%
- **Precision:** 0.889
- **Recall:** 0.800
- **F1 Score:** 0.842

*Sarcasm policy:* Detected irony is flagged and can redistribute emotion scores toward anger/disgust. This is a heuristic and may be wrong.

---

## 4. Latency Benchmarks (CPU Inference)

- **Mean Pipeline Latency:** `139.2 ms`
- **95th Percentile Latency:** `154.8 ms`

Latency measures the warm pipeline including template rationale, excluding startup, HTTP and persistence. Memory usage is not measured by this script. This small curated sample does not establish general accuracy.

---

## 5. Visual Performance Charts

![Evaluation Performance Charts](evaluation-charts.png)

## Run verification

Every hybrid case must use both transformers and embedding retrieval, or the evaluator aborts.

Parallel inference: True. Calibration profile: temperature_scaled.

Actual backend counts: `{'emotion_model_transformer': 70, 'sarcasm_model_transformer': 70, 'retrieval_rag_embeddings': 70}`. Confidence methods: `{'temperature_scaled': 69, 'uncalibrated_fusion': 1}`.
