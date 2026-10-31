# Operator handbook

See the [main README](../README.md) for setup, API contracts and measured results, and [deployment guide](deployment.md) for Waitress hosting and screenshots.

Use `python serve.py` for production serving. Models warm before requests. The platform supplies `PORT`; the default is 5000. Start with `USE_MODELS=1`, `LLM_MODE=mock`, `TORCH_NUM_THREADS=2`, `PARALLEL_INFERENCE=1` and `CALIBRATION_ENABLED=1`. Model downloads need internet once; cached operation can use `HF_HUB_OFFLINE=1`.

Restart after changing `.env`, model settings or the calibration profile. Never commit `.env`, model weights, logs or local databases. Use harmless sample sentences on the public demo because history is shared and there is no user authentication.

Check `/health` for loaded model capability and calibration-profile status. Inspect each result's route and warnings for the actual request path. An embedding query can fail while an embedding index remains loaded. Fallback results remain available with warnings and uncalibrated scores.

The UI and CSV report each record's confidence method. Temperature scaling is experimental and applies to English emotion scores with both transformers and embedding retrieval. Hindi/Hinglish normalization supports a small phrase vocabulary; all such results require review.

Use `/inspect` to review saved records and export CSV. Export uses a stable SQLite snapshot and neutralizes spreadsheet formula cells. Existing databases gain a confidence-method column while preserving records; old entries remain explicitly uncalibrated. A long export can briefly delay writers under SQLite's default journal mode.

Back up the SQLite file before a deployment change. Use a persistent volume for retained history; an ephemeral host may erase data on restart. Model caches may also be lost on an ephemeral instance.
