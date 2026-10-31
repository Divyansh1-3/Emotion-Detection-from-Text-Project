# P_098 Emotion Detection from Text

**Author: Divyansh Yadav** · HCL Industrial Training

Flask application combining pretrained emotion and sarcasm classifiers, linguistic rules and retrieved examples. It returns seven emotion scores, confidence, uncertainty, a sarcasm flag and an explanation. SQLite stores results for inspection and CSV export. This is linguistic tone analysis, not a clinical assessment.

## Setup

Use **Python 3.11+** with compatible dependency wheels. Virtual environments are machine-specific and excluded from Git.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe scripts/download_models.py
.\.venv\Scripts\python.exe -m backend.app.main
```

Open http://127.0.0.1:5000/. Models warm before the server accepts requests; startup may take tens of seconds. Downloading models requires internet once. Set `HF_HUB_OFFLINE=1` afterward for cached offline inference. `USE_MODELS=0` selects faster but less accurate heuristics.

`LLM_MODE=mock` uses local templates. Optional API explanations require `LLM_MODE=api`, a valid model ID, provider URL and API key. Never archive `.env`, databases, logs, environments or model weights. Rotate any key included in a previously shared archive.

Production WSGI serving:

```powershell
.\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:5000 --threads=2 backend.app.main:app
```

For hosted deployment, use `python serve.py`. It runs Waitress on `0.0.0.0` and honors the hosting platform's `PORT` variable, falling back to `FLASK_PORT` (5000). See [deployment and screenshot instructions](docs/deployment.md). The existing Flask application can be deployed directly; Matplotlib is used for evaluation charts and is not a hosting platform.

Docker uses Waitress and a Python HTTP health check. Container execution was not verified on the review host. Without a supplied model cache, its first startup requires model downloads. Set `USE_MODELS=0` for a lightweight smoke test.

## API

| Method | Path | Contract |
|---|---|---|
| POST | `/api/v1/emotion/process` | `{"input":"I am happy"}` |
| POST | `/api/v1/emotion/batch` | `{"texts":["happy","sad"]}` or CSV field `file` |
| GET | `/api/v1/emotion/results` | History with limit and offset |
| GET | `/api/v1/emotion/results/<id>` | One stored result |
| GET | `/api/v1/emotion/stats` | Counts and emotion distribution |
| GET | `/api/v1/emotion/export` | Download CSV |
| GET | `/health` | Loaded model and retrieval status |
| GET | `/inspect` | Paginated audit view and export |

Single responses contain `success`, `result`, `sources`, `warnings`, `request_id`. Batch responses identify original row numbers and attempted/succeeded/failed counts. Failed rows have an explicit error and no invented prediction. Valid rows are persisted with `mode=batch`. Limits: 4,000 characters, 500 rows and 16 MB uploads. Excess batches are rejected before processing. CSV accepts UTF-8 with/without BOM and text/sentence/input/utterance headers.

## Architecture

Flask routes → application service → bounded concurrent model inference → fusion → SQLite repository.

Flask is the chosen implementation framework. The supplied specification names FastAPI; this remains a declared deviation, documented in the SRS. Flask serves both the API and the existing dashboard.

1. Validate and preprocess once; reuse linguistic evidence.
2. Run rules, then run both classifiers and retrieval concurrently in a bounded three-worker pool.
3. Fuse scores, resolve approximate sarcasm, apply eligible English confidence calibration, and flag uncertainty.
4. Generate bounded explanation, harden output, persist and return.

Models: `j-hartmann/emotion-english-distilroberta-base`, `cardiffnlp/twitter-roberta-base-irony`, and `sentence-transformers/all-MiniLM-L6-v2`. Corpus: 82 exemplars and 8 knowledge entries. Retrieval falls back to TF-IDF and then keyword overlap. Charts are bundled locally.

Transformer fusion weights are 70% model, 15% rules and 15% retrieval; fallback weights differ. Top score < 0.40 or margin < 0.10 triggers uncertainty. Unsupported heuristic input also requires review. Detected sarcasm can shift emotion scores toward anger/disgust. Fusion weights remain hand-tuned; a fitted temperature adjusts eligible English emotion scores. The response, saved record, CSV and interface identify `confidence_method` as `temperature_scaled` or `uncalibrated_fusion`. A changed pipeline/model configuration disables an incompatible profile. Sarcasm scores remain uncalibrated. Transformer inputs truncate at 512 tokens. `TORCH_NUM_THREADS` defaults to 2. `PARALLEL_INFERENCE=0` disables concurrent inference. Restart after editing `.env`.

The LLM writes explanations only. Invalid JSON gets one retry before template fallback. Actual per-request backend choices and fallback warnings are recorded. `/health` describes loaded capability, so inspect an individual result for a query-specific fallback. CSV export reads one database snapshot to avoid duplicates or missing rows during concurrent inserts. Storage uses standard sqlite3; PostgreSQL, authentication and automatic WAL mode are not implemented.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/evaluate.py --mode hybrid
.\.venv\Scripts\python.exe scripts/evaluate.py --mode fallback
```

69 tests pass using temporary databases and no live API calls. Hybrid evaluation verifies all three model paths for every case, disables external LLM calls, records configuration, separates startup from warm latency and computes real pass/fail status. `--check` fails when a target is missed.

| Measurement | Hybrid | Heuristic + TF-IDF |
|---|---:|---:|
| Emotion macro-F1 | 0.913 | 0.471 |
| Emotion accuracy | 91.4% | 45.7% |
| Sarcasm F1 | 0.842 | 0.667 |
| Warm mean latency | 139.2 ms | 6.3 ms |

Each evaluation uses 35 curated cases per task. Hybrid startup was 16.1 seconds. The under-150 ms warm mean target is met **on this host**. Timings exclude startup, HTTP and persistence; hosted hardware and concurrent traffic need separate measurement. Memory and live-provider latency were not measured. Small-sample results do not establish general accuracy.

## Confidence calibration and language scope

Experimental temperature scaling was fitted on 700 GoEmotions dev examples and checked on 350 disjoint test examples. Calibration error fell from 17.4% to 4.2%; NLL and Brier score also improved. Label accuracy on this harder sample was 47.1% and does not improve through temperature scaling. The upstream emotion model used GoEmotions, so training overlap is unknown. This is limited domain calibration, not independent proof of general accuracy. See [method, caveats and reproduction](docs/calibration-report.md).

Common Hindi/Hinglish phrases and negation are normalized for the English models. The demo set matched 17/18 expected labels. These examples exercise supported phrases, not broad language coverage. All adapted and other non-English predictions remain uncertain and uncalibrated; Hindi/Hinglish sarcasm is not benchmarked. See [all language examples and the error](docs/language-evaluation.md).

See [evaluation](docs/evaluation-report.md), [raw results](docs/evaluation-results.json), [fallback evaluation](docs/evaluation-report-fallback.md) and [documentation](docs/P098_Formal_Project_Documentation.md).

## Submission

Submit the report and SRS, the GitHub link, and real screenshots of the local and deployed application. A ZIP and presentation are not required for this submission.

Repository: https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project

The report and SRS are in `docs/`, with submission copies in the workspace's `Submission-Ready` folder. Hosting and public-URL screenshots remain outstanding. Follow [deployment instructions](docs/deployment.md) after creating a hosting account and checking resource limits and pricing.
