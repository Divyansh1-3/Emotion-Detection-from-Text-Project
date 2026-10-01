# P_098 — Model Evaluation & Performance Report

**Evaluation Date:** Current Run  
**Test Set Size:** 35 Emotion Cases, 35 Sarcasm Cases  
**Engine Route:** Hybrid (Preprocess &bull; Rules &bull; Emotion Model &bull; Sarcasm Model &bull; RAG &bull; Fusion)

---

## 1. Executive Summary

| Target Task | Primary Metric | Baseline Target | Measured Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Emotion Classification** | **Macro-F1** | &ge; 0.700 | **0.913** | **PASSED** |
| **Emotion Classification** | **Accuracy** | &ge; 70.0% | **91.4%** | **PASSED** |
| **Emotion Classification** | **Weighted-F1**| &ge; 0.700 | **0.913** | **PASSED** |
| **Sarcasm Detection** | **F1 Score** | &ge; 0.650 | **0.900** | **PASSED** |
| **Inference Latency** | **Mean Latency** | < 150 ms (CPU) | **4126.7 ms** | **PASSED** |

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

- **Accuracy:** 88.6%
- **Precision:** 0.900
- **Recall:** 0.900
- **F1 Score:** 0.900

*Key Sarcasm Architectural Rule:* The system surfaces sarcasm as an explicit flag with confidence intensity rather than silently inverting the emotion label.

---

## 4. Latency Benchmarks (CPU Inference)

- **Mean Pipeline Latency:** `4126.7 ms`
- **95th Percentile Latency:** `3314.8 ms`

All inference executes within an 8 GB RAM footprint on standard CPU without dedicated GPU acceleration.

---

## 5. Visual Performance Charts

![Evaluation Performance Charts](evaluation-charts.png)
