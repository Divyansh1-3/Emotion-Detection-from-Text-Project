# P_098 — Emotion Detection from Text

A hybrid NLP service that reads a sentence and returns its **emotion**, a
**confidence** score, a **sarcasm** flag, and a short plain-English
**explanation** — combining a transformer model, deterministic linguistic rules,
and semantic retrieval so no single component can be wrong on its own.

> ⚠️ This is a linguistic **tone-analysis** instrument, **not** a clinical or
> psychological diagnostic tool.

---

## Overview

Given any English text, the API classifies it into one of **7 emotions** —
`anger`, `disgust`, `fear`, `joy`, `neutral`, `sadness`, `surprise` — and
returns a calibrated confidence, an *uncertain* badge when the signal is weak,
a sarcasm assessment, and a grounded rationale. Every result is persisted to
SQLite and viewable through a REST API or a server-rendered web UI.

The headline idea is a **hybrid pipeline**: a neural model gives the primary
signal, but hand-written rules and a retrieval "k-NN vote" are blended in to
correct it — and *every* stage has an offline fallback, so the app still runs
with no models downloaded and no API key configured.

## Key features

- 🧠 **Hybrid engine** — transformer (70%) + rule lexicon (15%) + RAG retrieval (15%), fused and calibrated.
- 🛟 **Graceful degradation** — transformer→heuristic, embeddings→TF-IDF→keyword, LLM→template. Nothing hard-fails.
- 🎭 **Sarcasm handling** — detects irony and *corrects the emotion* (e.g. fake praise over an adversity → anger/disgust, not joy).
- 📏 **Uncertainty calibration** — flags low-confidence or close-call predictions instead of overclaiming.
- 🔒 **Safety boundary** — strips prompt-injection, redacts clinical/diagnostic terms, always attaches a disclaimer.
- 🧾 **Full traceability** — every response records which engines ran and the route taken.
- 🌐 **REST API + Web UI + SQLite** — single-text and batch (JSON or CSV), plus a `/inspect` review dashboard.

## Architecture

```
HTTP request
   │
   ▼
api/routes/ ───────────► endpoints + Pydantic request validation
   │
   ▼
services/analysis_service.py ──► orchestrate · persist · log · batch
   │
   ▼
engines/router.py ──────► THE PIPELINE (runs every engine in order)
   │   validator · preprocess · rules · emotion_model · sarcasm_model
   │   retrieval(RAG) · fusion · llm(rationale) · validator(harden)
   ▼
repositories/results_repository.py ──► SQLite (read back by API + /inspect)
```

Layered, framework-light domain objects, and a clean separation of concerns
(*Application Factory*, *Blueprints*, *Service layer*, *Repository pattern*).

### The analysis pipeline (9 steps)

1. **Input validation** — trim, size-check, strip control chars, flag injection patterns.
2. **Preprocess** — demojize, expand slang, detect negation / CAPS / language.
3. **Rules** — lexicon emotion hints + a sarcasm-cue score (markers, praise⊕adversity contrast, punctuation, emoji).
4. **Emotion model** — DistilRoBERTa 7-way classifier *(→ heuristic fallback)*.
5. **Sarcasm model** — RoBERTa irony classifier *(→ rule-cue fallback)*.
6. **Retrieval (RAG)** — MiniLM embeddings over a knowledge base + k-NN vote *(→ TF-IDF → keyword fallback)*.
7. **Fusion & calibration** — blend signals, resolve sarcasm, apply emotion correction, decide confidence / uncertainty.
8. **Rationale** — bounded LLM explanation *(→ deterministic template fallback)*. Never overrides the label.
9. **Output hardening** — clamp scores, redact clinical terms, attach disclaimer, record route + latency.

## Tech stack

| Layer | Choice |
|---|---|
| Web / API | Flask 3, Pydantic v2 |
| Emotion model | `j-hartmann/emotion-english-distilroberta-base` |
| Sarcasm model | `cardiffnlp/twitter-roberta-base-irony` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Retrieval fallback | scikit-learn (TF-IDF + cosine) |
| LLM rationale | any OpenAI-compatible endpoint (OpenAI / Gemini / Ollama) |
| Storage | SQLite (stdlib `sqlite3`) |

## Project structure

```
P_098-emotion-detection-text-divyansh-yadav/
├── backend/app/
│   ├── __init__.py            # Flask application factory
│   ├── main.py                # entrypoint (warm-up + run server)
│   ├── api/routes/            # analysis API + /inspect views + /health
│   ├── core/                  # config (env) + logging
│   ├── domain/                # emotion schema, labels, value objects
│   ├── engines/               # the 9-step pipeline (router + engines)
│   ├── repositories/          # SQLite persistence
│   ├── schemas/               # Pydantic request models
│   └── services/              # pipeline orchestration
├── data/kb/                   # emotions.jsonl + exemplars.jsonl (RAG corpus)
├── frontend/                  # Jinja templates + static assets
├── prompts/                   # LLM system + task prompts
├── tests/                     # pytest suite
├── .env.example               # copy to .env
├── requirements.txt
└── pytest.ini
```

## Getting started

### Prerequisites
- **Python 3.10+**

### Installation

```powershell
# 1. From the project folder, create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate           # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your local config
copy .env.example .env                # Windows
# cp .env.example .env                # macOS / Linux
```

### Models

On the first run with `USE_MODELS=1`, the transformer and embedding models are
downloaded automatically from Hugging Face into your local cache; later runs can
set `HF_HUB_OFFLINE=1` to load them from cache without any network calls.

Don't want the downloads (or offline)? Set `USE_MODELS=0` in `.env` to run the
pipeline in **fast heuristic mode** — it uses the rule lexicon + TF-IDF and
still returns full, valid results.

### Run

```powershell
python -m backend.app.main
```

- Web dashboard → <http://127.0.0.1:5000/>
- Inspection view → <http://127.0.0.1:5000/inspect>
- Health check → <http://127.0.0.1:5000/health>

## Configuration

All settings are read from `.env` (see `.env.example`). The app runs with zero
configuration — every value has a sensible default.

| Variable | Default | Purpose |
|---|---|---|
| `LLM_MODE` | `mock` | `api` = call the LLM; `mock` = offline template rationale |
| `OPENAI_API_KEY` | *(empty)* | key for the LLM; blank forces offline mode |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | any OpenAI-compatible endpoint |
| `OPENAI_MODEL` | `gpt-4o-mini` | model name for the rationale |
| `USE_MODELS` | `1` | `0` = skip transformers, use heuristic/TF-IDF |
| `EMOTION_MODEL` / `SARCASM_MODEL` / `EMBEDDING_MODEL` | *(see above)* | Hugging Face model ids |
| `UNCERTAIN_THRESHOLD` | `0.40` | below this top-score (or small margin) → *uncertain* |
| `SARCASM_THRESHOLD` | `0.50` | sarcasm flag cutoff |
| `RETRIEVAL_TOP_K` | `5` | exemplars retrieved per query |
| `DATABASE_URL` | `sqlite:///emotion.sqlite3` | persistence target |
| `FLASK_HOST` / `FLASK_PORT` | `127.0.0.1` / `5000` | server bind |
| `MAX_INPUT_CHARS` / `MAX_BATCH_ROWS` | `4000` / `500` | request limits |

> 🔐 **Never commit your real `.env`.** It's already in `.gitignore`. Keep API keys out of version control.

## API reference

Base path: `/api/v1/emotion`

### `POST /process` — analyze one text

```bash
curl -X POST http://127.0.0.1:5000/api/v1/emotion/process \
  -H "Content-Type: application/json" \
  -d '{"input": "Oh great, my train got cancelled again. Just what I needed."}'
```

```jsonc
{
  "success": true,
  "result": {
    "primary_emotion": "anger",
    "confidence": 0.62,
    "uncertain": false,
    "sarcasm": true,
    "sarcasm_score": 0.99,
    "emotion_scores": [{"label": "anger", "score": 0.62}, {"label": "disgust", "score": 0.19}],
    "rationale": "The text exhibits sarcastic tone cues with irony...",
    "route": ["input_validation", "preprocess", "rules", "emotion_model_transformer", "..."]
  },
  "sources": [ ... ],
  "warnings": [ ... ],
  "request_id": "req_xxxxxxxxxxxx"
}
```

### `POST /batch` — analyze many
JSON list: `{"texts": ["...", "..."]}`  ·  or a CSV upload (multipart field `file`,
auto-detecting a `text`/`sentence`/`input` column).

### Other endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/emotion/results?limit=&offset=` | paginated history |
| `GET` | `/api/v1/emotion/results/<id>` | one stored analysis |
| `GET` | `/api/v1/emotion/stats` | totals + emotion distribution |
| `GET` | `/health` | service + model status |

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests run **offline and fast** (`conftest.py` sets `USE_MODELS=0`, `LLM_MODE=mock`)
and cover the rules, validator, fusion/calibration, API, and red-team safety cases.

## How it works — fusion & sarcasm

The emotion/sarcasm **labels are decided deterministically** in `fusion.py`; the
LLM only writes the explanation. Fusion blends the three signals, then:

- resolves sarcasm from the irony model **and** rule cues (guarding genuine joy/sadness/neutral against false positives), and
- when sarcasm is detected, **discounts the superficial masking emotions** (joy / surprise / neutral / sadness) and shifts that weight to **anger / disgust** — so ironic praise over a mishap is read correctly.

## Limitations

- Optimized for **English**; other languages fall back to weaker signals.
- Fusion sarcasm thresholds are hand-tuned heuristics, not learned.
- Batch is processed sequentially (simple and predictable, not high-throughput).
- **Not** a clinical, medical, or psychological assessment tool.

---

**Project:** P_098 — Emotion Detection from Text · **Author:** Divyansh Yadav
