# Deployment and submission screenshots

The submission needs screenshots of the working application, screenshots from its deployed URL, documentation containing the GitHub link, and the SRS. A source ZIP is not required for this submission.

GitHub repository: https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project

The application uses Flask. Matplotlib generates the evaluation figures in `docs/evaluation-charts.png` and `docs/evaluation-charts-fallback.png`; it does not deploy the application. A Streamlit rewrite is not needed to host the existing interface.

## Production startup

Use Python 3.11 with the project dependencies, then start:

```text
python serve.py
```

The server uses Waitress, binds to `0.0.0.0`, reads the platform's `PORT`, and uses two request threads. Without `PORT`, it uses `FLASK_PORT` or port 5000. Models warm before the server accepts requests. Allow enough startup time for first-time model downloads.

| Variable | Full model demo value | Purpose |
|---|---|---|
| `USE_MODELS` | `1` | Enable both classifiers and embedding retrieval |
| `LLM_MODE` | `mock` | Generate local explanations without a provider key |
| `HF_HUB_OFFLINE` | `0` | Allow the initial model download |
| `TORCH_NUM_THREADS` | `2` | Limit CPU thread contention |
| `PORT` | Assigned by host | HTTP listen port |
| `DATABASE_URL` | `sqlite:///emotion.sqlite3` | Demo history; use a mounted path if persistent storage is available |

Keep the actual `.env`, local databases, logs, and virtual environment out of GitHub and the deployed build. Use harmless example sentences for a public demo: the application exposes history to visitors and does not implement user accounts. Storage on an ephemeral host resets on restart, so capture the history screenshots during the same demo session.

## Hosting choices

A host must have enough memory for two transformer classifiers plus the embedding model. Successful deployment means the model paths work, not just that an HTTP page loads. Avoid promising the full model demo on a small free instance without measuring its memory use.

For a Python web service such as Render, the build command is `pip install -r requirements.txt` and the start command is `python serve.py`. Set the health-check path to `/health`. Choose hardware only after checking its memory limits and price. Render supports Flask directly and provides an HTTPS service URL.

The repository also has a Dockerfile with a non-root user, writable model-cache location, host-assigned port support, and an extended startup health-check grace period. For a Hugging Face Docker Space, set the Space README metadata to `sdk: docker` and `app_port: 5000`, matching the default application port. Hugging Face documentation checked on 1 November 2026 says creating Docker Spaces requires a paid plan even though CPU Basic has no hourly charge. Do not treat it as an unconditional free hosting option.

If using `USE_MODELS=0` on limited hardware, identify the deployed application as a heuristic fallback demonstration. Do not present that deployment as reproducing the transformer evaluation results.

Official hosting references:

- https://render.com/docs/deploy-flask
- https://render.com/docs/free
- https://huggingface.co/docs/hub/spaces-overview
- https://huggingface.co/docs/hub/spaces-sdks-docker

## Verify the deployed application

1. Push the reviewed local source and required supporting files to the GitHub repository; a link alone does not upload local edits.
2. Deploy the intended GitHub commit on the chosen host.
3. Open the public HTTPS URL and submit a new sentence.
4. Check `/health`: `emotion_loaded` and `sarcasm_loaded` should both be true, and `retrieval_backend` should be `embeddings` for the full model demo.
5. Run a short batch, inspect a saved result, and download the CSV export.
6. Record the deployed URL, commit, and actual backend mode alongside the screenshots. Add the live URL to the documentation only after it has been verified.

## Screenshot checklist

Capture real browser views with readable text. For deployment evidence, keep the public URL visible in the address bar.

| Screenshot | What to show |
|---|---|
| Dashboard | Application title, input controls and navigation |
| Single analysis | A fresh sentence such as `I am delighted to see my family!`, its actual result, score chart and explanation |
| Sarcasm example | Input, actual sarcasm assessment and any uncertainty warning; do not change labels to fit an expected result |
| Batch analysis | A small CSV with several examples and the returned row statuses |
| Saved history | `/inspect` showing results created during the demo |
| Record detail | Saved input, scores, execution route and retrieved evidence |
| Deployed model status | `/health` at the public URL showing actual model and retrieval status |
| Evaluation figure, if requested | The existing Matplotlib chart, identified as local evaluation evidence rather than proof of deployment |

The prepared report and SRS are in the workspace's `Submission-Ready` folder. The app is not considered deployed until a working public URL and its actual inference paths have been checked. Browser screenshots must come from the working pages, not reconstructed images.
