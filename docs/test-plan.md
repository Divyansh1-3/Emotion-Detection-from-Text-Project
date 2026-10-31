# Test plan and verification record

Author: Divyansh Yadav

Run `python -m pytest -q`. The current suite has 69 passing tests, including rule/fusion/validator units, API and SQLite integration, adversarial strings, malformed batch schemas, atomic limits, BOM CSV headers, explicit row errors, sincere positive phrases, unknown fallback uncertainty, CSV export escaping, isolated application databases and malformed LLM responses, snapshot export under concurrent inserts, actual retrieval fallback traces, stale-index reload, confidence-profile safeguards, legacy database migration and Hindi/Hinglish normalization/negation.

Tests use temporary SQLite files and disable models and live API calls. Full model evaluation is separate: `python scripts/evaluate.py --mode hybrid`. Fallback evaluation uses `--mode fallback`. Run configurations and raw results are saved in docs/evaluation-results*.json. Target failures are preserved rather than reclassified as passes.

Scope limits: the dataset has 35 curated cases per task. Automated tests do not establish broad semantic accuracy, production security, live-provider availability or cross-platform Docker/browser behavior.

Production smoke verification starts `serve.py` on an assigned PORT with both transformers and embeddings, submits an HTTP analysis, checks detail rendering and verifies that the calibration method survives persistence and CSV export. Docker and deployed browser checks remain separate.
