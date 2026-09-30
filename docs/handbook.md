# P_098 — Emotion Detection from Text: Product Handbook

> **Project Code:** P_098  
> **Candidate:** Divya  
> **Industrial Training:** HCL Technologies  
> **Release:** v1.0.0  
> **Architecture:** Hybrid Multi-Engine (Rules + Transformers + RAG + Fusion + Bounded LLM)  
> **Framework:** Flask 3.0 &bull; PyTorch CPU &bull; Transformers &bull; SQLite

---

## Table of Contents
1. [Overview & Target Personas](#1-overview--target-personas)
2. [Core Concepts & Taxonomies](#2-core-concepts--taxonomies)
3. [The 6 Hybrid Engines Architecture](#3-the-6-hybrid-engines-architecture)
4. [End-to-End Pipeline Walkthrough](#4-end-to-end-pipeline-walkthrough)
5. [Frontend &harr; Backend Parity & The `/inspect` View](#5-frontend-backend-parity--the-inspect-view)
6. [API Reference & Contract](#6-api-reference--contract)
7. [RAG Implementation & Justification](#7-rag-implementation--justification)
8. [Configuration & Deployment](#8-configuration--deployment)
9. [Safety Boundaries & Non-Diagnostic Limits](#9-safety-boundaries--non-diagnostic-limits)
10. [Troubleshooting & FAQ](#10-troubleshooting--faq)
11. [System Glossary](#11-system-glossary)

---

## 1. Overview & Target Personas

### 1.1 Purpose
`P_098 Emotion Detection from Text` is an industrial-grade NLP classification and audit system. It analyzes raw text utterances to identify the predominant affective state across 7 discrete emotion categories (`anger`, `disgust`, `fear`, `joy`, `neutral`, `sadness`, `surprise`), detects ironic/sarcastic nuances, computes a calibrated confidence margin, and generates a grounded 1–2 sentence explanation.

It is designed strictly as an **analytical instrument for linguistic tone**, not a clinical psychiatric diagnostic tool.

### 1.2 Target Personas
1. **Customer Experience (CX) Escalation Lead:** Triage high-anger and sarcastic customer complaints to human agents before churn occurs.
2. **Social Media & Brand Listening Analyst:** Classify public sentiment beyond binary positive/negative into fine-grained emotional responses.
3. **Conversational AI Auditor:** Evaluate chatbot transcripts to detect customer frustration, sarcasm, or confusion during automated dialogues.

---

## 2. Core Concepts & Taxonomies

### 2.1 The 7-Label Emotion Schema
The system maps all utterances into one of 7 standardized emotion classes:
* 😄 **Joy:** Happiness, celebration, contentment, relief, delight, affection.
* 😠 **Anger:** Frustration, annoyance, resentment, rage, indignation.
* 😢 **Sadness:** Sorrow, disappointment, heartbreak, loneliness, grief.
* 😨 **Fear:** Anxiety, panic, apprehension, dread, vulnerability.
* 😮 **Surprise:** Shock, amazement, astonishment, sudden realization.
* 🤢 **Disgust:** Revulsion, aversion, distaste, moral outrage.
* 😐 **Neutral:** Factual statements, objective announcements, questions, routine remarks.

### 2.2 Sarcasm: Explicit Flagging vs. Silent Inversion
A foundational architectural rule in P_098 is: **Sarcasm is surfaced as an explicit warning flag with an intensity score, never used to silently flip the predicted emotion.**
* *Example:* "Oh fantastic, another delayed flight. Just marvelous."
* *Behavior:* The model detects positive lexicon ("fantastic", "marvelous") clashing with situational context and punctuation markers (`...`, `!`). It outputs `primary_emotion: anger` or `neutral`, flags `sarcasm: True`, and highlights the conflict in the grounded rationale.

### 2.3 Uncertainty Calibration & Margin
Raw model probabilities are often overconfident. P_098 calculates:
$$\text{Margin} = P(\text{Top}_1) - P(\text{Top}_2)$$
An utterance is automatically stamped as **Uncertain** if:
$$P(\text{Top}_1) < 0.40 \quad \text{OR} \quad \text{Margin} < 0.10$$
When flagged as uncertain, downstream human reviewers are alerted.

---

## 3. The 6 Hybrid Engines Architecture

```
User Utterance (Text / CSV)
       │
       ▼
[ 1. Input Validator ] ──> Sanitization, Injection Filter, Size Cap
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
[ 2. Deterministic Rules ]              [ 3. Transformer Models ]
  - Emoji Normalization                   - DistilRoBERTa (Emotion)
  - Slang & Negation Handling             - RoBERTa (Sarcasm)
  - Punctuation/Caps Cues                        │
       │                                         │
       ├─────────────────────────────────────────┘
       ▼
[ 4. Semantic RAG Engine ] ──> FAISS/Cosine Search over Exemplar & KB Index
       │                        (Yields k-NN vote + Grounding Snippets)
       ▼
[ 5. Signal Fusion & Calibration ]
       - Blends: 70% Transformer + 15% Rules + 15% k-NN
       - Calibrates Margin & Uncertainty Badge
       - Resolves Sarcasm Score
       - Deterministic Label Decision (NOT decided by LLM)
       │
       ▼
[ 6. Bounded LLM Rationale ] ──> Generates Grounded 1-2 Sentence Explanation
       │                          (Offline Deterministic Template Fallback)
       ▼
[ Output Hardening & Storage ] ──> SQLite (analyses table) + Structured Log
       │
       ├───────────────────────┬───────────────────────┐
       ▼                       ▼                       ▼
Interactive Dashboard      Server-Side /inspect      JSON API Clients
```

### The Engine Roles:
1. **`preprocess.py` & `rules.py`:** Deterministic, zero-dependency linguistic analysis. Extracts emojis, maps slang, evaluates negation windows, and tallies sarcastic punctuation contrast.
2. **`emotion_model.py`:** Pretrained transformer (`j-hartmann/emotion-english-distilroberta-base`) running on CPU, yielding probability distributions across 7 classes.
3. **`sarcasm_model.py`:** Specialized sequence classifier (`helinivan/english-sarcasm-detector`) outputting sarcasm probability.
4. **`retrieval.py`:** Semantic search over curated exemplars and emotion definitions. Provides a k-NN calibration vote and factual context snippets.
5. **`fusion.py`:** Combines the signals with deterministic weighting, computes decision margins, and flags uncertainty.
6. **`llm.py`:** Consumes input text, computed labels, and retrieved evidence to generate human-readable explanations via OpenAI-compatible API or offline template.
7. **`validator.py`:** Enforces schema invariants, prompt-injection defenses, and strips prohibited psychiatric diagnostic claims.

---

## 4. End-to-End Pipeline Walkthrough

1. **Ingress:** Utterance enters via `POST /api/v1/emotion/process` or dashboard UI.
2. **Input Hygiene:** Validator checks $1 \le \text{length} \le 4000$ characters, strips ASCII control codes, and scans for instruction overrides.
3. **Feature Extraction:** Preprocessor decodes emojis into textual tokens and detects negation operators.
4. **Inference:** Transformer pipelines evaluate emotion and sarcasm probabilities in parallel threads.
5. **Retrieval Grounding:** Query is embedded to fetch top-3 nearest exemplars and relevant KB definitions.
6. **Mathematical Fusion:** Probabilities are fused into a normalized distribution; top-two margin is checked for uncertainty.
7. **Rationale Synthesis:** The bounded LLM synthesizes an explanation grounded in the retrieved sources without altering labels.
8. **Persistence:** Transaction is assigned a UUID `request_id`, timed for latency, and persisted to SQLite.
9. **Egress:** Returns structured JSON to the client.

---

## 5. Frontend &harr; Backend Parity & The `/inspect` View

### 5.1 Single Source of Truth
The client dashboard performs **no metrics calculation**. All labels, probabilities, badges, routes, and latencies are computed on the backend, saved to SQLite, and rendered from that exact record.

### 5.2 The `/inspect` Audit View
Auditors and teachers can access `http://127.0.0.1:5000/inspect` to examine all historical transactions directly from the database:
* Complete utterance text
* Predicted emotion and calibrated confidence
* Sarcasm flag and intensity score
* Uncertainty status
* Exact execution route trace (`input_validation` &rarr; `rules` &rarr; `emotion_model` &rarr; `retrieval` &rarr; `fusion` &rarr; `rationale`)
* Microsecond latency telemetry

---

## 6. API Reference & Contract

### 6.1 `POST /api/v1/emotion/process`
Analyze a single text utterance.

**Request:**
```json
{
  "input": "I just received the promotion I worked towards for two full years! Celebrating tonight! 🎉",
  "session_id": "sess_102",
  "options": {}
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "request_id": "req_8f12a9e3b4c1",
  "result": {
    "input_text": "I just received the promotion I worked towards for two full years! Celebrating tonight! 🎉",
    "primary_emotion": "joy",
    "confidence": 0.942,
    "uncertain": false,
    "sarcasm": false,
    "sarcasm_score": 0.041,
    "rationale": "The text exhibits strong alignment with 'joy' markers, reflecting celebration and career milestone achievement.",
    "latency_ms": 68.4,
    "route": [
      "input_validation",
      "preprocess",
      "rules",
      "emotion_model_transformer",
      "sarcasm_model_transformer",
      "retrieval_rag",
      "fusion_calibration",
      "rationale_template_fallback",
      "output_validation"
    ],
    "emotion_scores": [
      {"label": "joy", "score": 0.942},
      {"label": "surprise", "score": 0.031},
      {"label": "neutral", "score": 0.015},
      {"label": "sadness", "score": 0.005},
      {"label": "fear", "score": 0.003},
      {"label": "anger", "score": 0.002},
      {"label": "disgust", "score": 0.002}
    ]
  },
  "sources": [
    {
      "source": "exemplar",
      "label": "joy",
      "similarity": 0.812,
      "text": "I just received the promotion I worked towards for two full years! Celebrating tonight!"
    }
  ],
  "warnings": [
    "Analysis reflects automated linguistic tone analysis and is not a clinical or psychological evaluation."
  ]
}
```

### 6.2 `POST /api/v1/emotion/batch`
Analyze a batch of texts via CSV file upload (`multipart/form-data`) or JSON array:
```json
{
  "texts": [
    "Great work team!",
    "Flight delayed for 4 hours with no food.",
    "The meeting is scheduled for 3 PM."
  ]
}
```

### 6.3 `GET /api/v1/emotion/results`
Returns paginated SQLite records with `?limit=50&offset=0`.

### 6.4 `GET /api/v1/emotion/stats`
Returns system aggregate metrics: total runs, uncertain count, sarcastic count, average confidence, and emotion frequency distribution.

### 6.5 `GET /health`
Returns system operational health, model load status, and configured LLM provider mode.

---

## 7. RAG Implementation & Justification

### 7.1 Why RAG in a Classification Project?
In text classification, RAG serves two critical, defensible purposes:
1. **Evidence Grounding for LLM Rationale:** Rather than letting an LLM hallucinate reasons for why a text feels "sad" or "angry", the RAG engine retrieves verified dictionary definitions and annotated exemplars that the LLM must cite.
2. **Confidence Calibration via k-NN Vote:** Retrieved exemplars act as a non-parametric nearest-neighbor voting mechanism. If a transformer predicts "anger" with 60% probability, but 5 nearest exemplars in the knowledge base are labelled "disgust", the fused confidence is adjusted and the case is correctly flagged for manual audit.

---

## 8. Configuration & Deployment

### 8.1 Environment Variables (`.env`)
| Key | Default | Description |
| :--- | :--- | :--- |
| `LLM_MODE` | `mock` | `api` to call OpenAI-compatible endpoint, `mock` for offline template |
| `OPENAI_API_KEY` | `""` | API key. If empty, system automatically operates in mock mode |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Endpoint URL (supports Ollama, vLLM, Azure OpenAI) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name for rationale synthesis |
| `UNCERTAIN_THRESHOLD` | `0.40` | Confidence floor below which uncertain badge fires |
| `SARCASM_THRESHOLD` | `0.50` | Blended score above which sarcasm flag fires |
| `DATABASE_URL` | `sqlite:///emotion.sqlite3` | SQLite path or PostgreSQL connection string |
| `USE_MODELS` | `1` | `1` to run transformers, `0` for pure heuristic mode |

### 8.2 Production Container (`Dockerfile`)
The repository includes a multi-stage, non-root Dockerfile running Gunicorn:
```bash
docker build -t p098-emotion-detector .
docker run -p 5000:5000 p098-emotion-detector
```

---

## 9. Safety Boundaries & Non-Diagnostic Limits

1. **Non-Diagnostic Policy:** The system assesses linguistic patterns in text utterances. It has no access to physiological, biological, or psychiatric diagnostic criteria.
2. **Clinical Term Redaction:** The validator scans every output rationale and strips clinical terms (`depression`, `bipolar`, `schizophrenia`, `self-harm`) to prevent users from mistaking text classification for medical advice.
3. **Universal Disclaimer:** Every API response and UI report contains:  
   *"Analysis reflects automated linguistic tone analysis and is not a clinical or psychological evaluation."*
4. **Prompt Injection Hardening:** User utterances are treated as raw data variables within strict JSON schemas, never as executable prompt directives.

---

## 10. Troubleshooting & FAQ

**Q: Can I run this completely offline without internet or an OpenAI API key?**  
*A: Yes! With `LLM_MODE=mock` and empty `OPENAI_API_KEY`, the app runs 100% locally on CPU using local transformers (or heuristic rules) and deterministic template rationales.*

**Q: How does this run on an 8 GB RAM laptop?**  
*A: We use DistilRoBERTa (~330 MB) and all-MiniLM-L6-v2 (~80 MB) with PyTorch CPU inference. Total memory footprint remains under 1.2 GB.*

**Q: Where are the stored records saved?**  
*A: In `emotion.sqlite3` at the project root. You can view them in the browser at `/inspect` or open the database directly with any SQLite viewer.*

---

## 11. System Glossary
* **Affective Computing:** The study and development of systems that can recognize and interpret human emotions.
* **Calibrated Confidence:** Probability score adjusted for model uncertainty, top-two margin, and exemplar agreement.
* **Grounding Evidence:** Reference documents or exemplars that provide verifiable justification for an AI decision.
* **Hybrid Engine:** An architecture combining symbolic rules, pretrained deep learning, semantic retrieval, and bounded generative AI.
* **Macro-F1:** The unweighted mean of F1-scores across all emotion classes, ensuring minority classes are evaluated fairly.
