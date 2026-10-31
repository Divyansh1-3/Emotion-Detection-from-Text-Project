# Emotion and Sarcasm Detection from Text

An English-only Streamlit project by **Divyansh Yadav** for HCL Industrial Training.
The application classifies **emotion and sarcasm/irony using two pretrained transformers**.

Enter a sentence and click **Analyze text**. The dashboard shows seven emotion scores,
a separate sarcasm assessment, session counts, the latest ten results, and **Save result**.
Sarcasm does not automatically change the emotion label.

## Models

| Task | Pretrained checkpoint | Output |
|---|---|---|
| Emotion | [j-hartmann/emotion-english-distilroberta-base](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) | anger, disgust, fear, joy, neutral, sadness, surprise |
| Sarcasm indicator | [cardiffnlp/twitter-roberta-base-irony](https://huggingface.co/cardiffnlp/twitter-roberta-base-irony) | non-irony and irony |

The irony model was fine-tuned on TweetEval. Irony is used as a **proxy for sarcasm**;
it does not reliably identify every form of sarcasm, humor, or dismissiveness.
The exact model revisions are pinned in `emotion_model.py`.
The models run on CPU in float16 to reduce weight memory, with two compute threads.
Concurrent inference is serialized to bound activation memory.
Models are shared across sessions; user input and results are not cached globally.

There is **no TF-IDF or rule-based fallback**. If either transformer cannot load or run,
the app reports an error and does not save a partial or fabricated analysis.
The UI summary describes scores and their limits; it does not claim to attribute
individual words to transformer decisions.

## Run locally

Use Python 3.13. From this repository folder:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

For an existing environment, rerun the **pip install** command: the former
Streamlit/scikit-learn-only environment does not contain the new model dependencies.
Then use `start_app.bat` or the Streamlit command and open http://localhost:8501.

The local Windows Python 3.13 environment was verified on 1 November 2026 with
PyTorch 2.14.0+cpu and Transformers 5.18.0. Dependency checks, all 22 tests, and
a dashboard smoke check using real cached models passed. See [verification status](docs/verification.json).

On Linux/macOS, use `python3.13 -m venv .venv` and `.venv/bin/python`.
The requirements select CPU-only PyTorch wheels on Linux/Windows. No API key is needed.

**First model use downloads about 827 MB of weights**, plus tokenizer/config files,
from Hugging Face. Allow time for downloading and loading. Downloads are cached on the host;
a fresh cloud container may need to download again. To load them before opening the UI:

```powershell
.\.venv\Scripts\python.exe -c "from emotion_model import load_models; load_models()"
```

Once the packages and both pinned model checkpoints are cached, inference can work offline.
Set `HF_HUB_OFFLINE=1` to require cache-only operation. Inference runs on the app's host,
not a paid model API. A cloud visit necessarily sends the entered text to your app server.

## Public deployment

[Public app](https://emotion-detection-from-text-project-ncignaopdfgyjcymc264jq.streamlit.app/)

The transformer implementation is published as commit `7f159b6`. Its
[GitHub Actions workflow](https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project/actions/runs/41246313817)
passed, including dependency installation and both test suites. On 1 November 2026,
the owner confirmed uploading and testing the updated public app successfully.
This is owner-reported deployment verification; an independent live browser check
was unavailable. The earlier private-window check covered the previous app version.

Keep repository `Divyansh1-3/Emotion-Detection-from-Text-Project`, branch `main`,
entrypoint `app.py`, Python `3.13`, and no secrets. Follow [deployment.md](docs/deployment.md).
Transformers increase download size, RAM use, and startup time. Free hosting can sleep
or exceed its resource limits; no instant-start or resource-fit guarantee is made.

## Interpreting results

- Emotion scores cover seven labels. Love is no longer a separate label.
- An emotion is marked uncertain when its top score is below 45%, or its lead is under 10 percentage points.
- Sarcasm/irony score at least 80%: **Likely sarcasm**; at most 20%: **Sarcasm not detected**;
  between those thresholds: **Uncertain**. These are display thresholds, not empirical calibration.
- The emotion may reflect literal wording even when the irony model flags sarcasm.
- The model can flag sincere statements and miss dry humor. In particular, it currently misses
  the sarcastic intent in **“I am busy right now, can I ignore you some other time?”**
  This observed limitation is recorded rather than treated as a passing sarcasm example.
- English letters are checked; other languages written in Latin letters are not reliably detected.
  Inputs are limited to 1,000 characters and 512 tokens per model. Excess tokens are rejected,
  not silently truncated.
- This student demo does not determine a person's mental state.

History is limited to ten entries per browser session. Summary counts cover all successful
analyses since reset. **Clear text** clears the input/current result; **Reset session**
also clears history and counters. Downloaded results include both assessments and model revisions.

## Verification

```powershell
# Fast contract/dashboard tests with controlled model outputs:
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

# Real pretrained model integration checks:
$env:RUN_TRANSFORMER_TESTS='1'
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_transformers.py -v

# Run the small project regression set and write its full results:
.\.venv\Scripts\python.exe evaluate_transformers.py
```

The CI workflow runs both the fast tests and real-model integration.
[Transformer evaluation](docs/transformer-evaluation.json) records 35 emotion and 35 sarcasm
regression examples and known failures. These hand-written, previously reviewed examples
are **not an independent benchmark**. The report distinguishes raw binary argmax metrics
from the dashboard's uncertain category.

The old **88.2% accuracy / 0.842 macro-F1** figures, `model/emotion_model.pkl.gz`,
`model/evaluation.json`, compressed DAIR-AI data, and `train_model.py` belong to the
historical TF-IDF baseline. They are not used by the current app or evidence for its accuracy.
The historical training script requires scikit-learn 1.9.1 separately.
See [verification status](docs/verification.json) for the scope of this revision's checks.

## Submission documents

The [report, SRS and synopsis](docs/README.md) are revised for the transformer
implementation, with all 13 rendered pages checked. They include current model
details, regression results, deployment evidence and the known sarcasm limitation.
The revised documents and current local runtime verification are included in this repository.
