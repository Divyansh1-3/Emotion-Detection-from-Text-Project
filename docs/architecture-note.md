# P_098 — Technical Architecture & Engineering Decisions

**Project:** P_098 Emotion Detection from Text  
**Author:** Divya  
**Target Environment:** 8 GB RAM Developer Laptop &bull; CPU-Only Inference &bull; Python 3.11

---

## 1. Core Architectural Pillars

### 1.1 Determinism Over Generation
A critical design decision in P_098 is that **the primary emotion label is determined strictly by deterministic mathematics (fusion.py), never by the Large Language Model (llm.py).**
* *Why:* Large Language Models are stochastic. Prompting an LLM to "classify emotion" leads to non-reproducible outputs, hallucinated labels outside the schema, and vulnerability to prompt injection.
* *How P_098 solves this:* Pretrained transformers output logit distributions; symbolic rules evaluate punctuation and negations; RAG fetches k-NN exemplar votes. The fusion module normalizes these into a mathematical distribution. The LLM's only role is generating a human-readable 1–2 sentence explanation grounded in the retrieved evidence.

### 1.2 Resource Management & 8 GB RAM Sizing
Deploying transformer models on commodity hardware requires disciplined memory allocation:
1. **Model Selection:**
   * Emotion: `j-hartmann/emotion-english-distilroberta-base` (~330 MB)
   * Sarcasm: `helinivan/english-sarcasm-detector` (~300 MB)
   * Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (~80 MB)
   * *Total model weights:* ~710 MB in memory.
2. **Lazy Thread-Safe Singletons:** Models are loaded into process memory only on the first inference request behind thread locks, preventing multi-worker memory multiplication.
3. **CPU PyTorch:** Built without heavy CUDA runtime dependencies.

---

## 2. Signal Fusion Mathematics

The fused probability for each emotion label $e \in \text{EMOTION\_LABELS}$ is calculated as:

$$P_{\text{fused}}(e) = w_{\text{ml}} \cdot P_{\text{ml}}(e) + w_{\text{rule}} \cdot P_{\text{rule}}(e) + w_{\text{knn}} \cdot P_{\text{knn}}(e)$$

Where default weights are:
* $w_{\text{ml}} = 0.70$ (Deep transformer probability)
* $w_{\text{rule}} = 0.15$ (Deterministic lexicon & negation cues)
* $w_{\text{knn}} = 0.15$ (Retrieved exemplar nearest-neighbor vote)

When offline or in heuristic mode:
* $w_{\text{ml}} = 0.0$
* $w_{\text{rule}} = 0.60$
* $w_{\text{knn}} = 0.40$

### Margin Calibration:
Let $e_{(1)}$ be the highest scoring emotion and $e_{(2)}$ be the second highest:
$$\Delta = P_{\text{fused}}(e_{(1)}) - P_{\text{fused}}(e_{(2)})$$

The utterance is flagged as **Uncertain** if:
$$P_{\text{fused}}(e_{(1)}) < \tau_{\text{uncertain}} \quad (0.40) \quad \lor \quad \Delta < 0.10$$

---

## 3. Concurrency & SQLite Persistence

* SQLite is accessed via thread-safe connections with Python's `threading.Lock`.
* Transactions are committed synchronously to maintain immediate consistency between the JSON API and the server-rendered `/inspect` dashboard.
* The persistence abstraction (`ResultsRepository`) cleanly isolates database logic, allowing production swapping to PostgreSQL simply by changing `DATABASE_URL=postgresql://user:pass@host/db`.
