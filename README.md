# Emotion Detection from Text

A small English-only machine-learning project by **Divyansh Yadav** for HCL Industrial Training.

Enter a sentence, click **Analyze emotion**, and explore the result in a dashboard with input and output side by side. The six emotions are **joy, sadness, anger, fear, love, and surprise**.

The dashboard includes session summary cards, a color-coded score chart, an explanation based on contributing words, the 10 most recent analyses, and a **Save result** text download. **Clear text** clears the input; **Reset session** clears the results and summary counts. Everything runs locally without an API key.

## Run on your computer

Use **Python 3.13**. In a terminal inside this project folder, run these commands once:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then double-click **start_app.bat**, or run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open **http://localhost:8501**. Keep the terminal open while using the app; press **Ctrl+C** to stop it. The trained model is included, so you do not need to train anything or create an API key. After installing the packages, the local app works without internet.

On Linux/macOS, use `python3.13 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, and `.venv/bin/python -m streamlit run app.py`.

## Deploy for free

Use [Streamlit Community Cloud](https://share.streamlit.io/). It gives the app a shareable web link, and visitors do not need Python installed.

Create an app from this GitHub repository with:

| Setting | Value |
|---|---|
| Repository | `Divyansh1-3/Emotion-Detection-from-Text-Project` |
| Branch | `main` |
| Main file | `app.py` |
| Python version, under Advanced settings | `3.13` |
| Secrets | None needed |

See [the short deployment guide](docs/deployment.md). Hosting requires a Streamlit account linked to GitHub. A deployment configuration is not a live deployment; Streamlit provides the final URL after deployment succeeds.

Free apps can sleep when unused. The first visitor may need to wake the app and wait. The model is already trained and only about **655 KiB**, so there are no model downloads or training jobs during startup. This does not guarantee a particular opening time on free hosting.

## How it works

1. Check that the input contains words and is at most 1,000 characters.
2. **TF-IDF** converts words and pairs of words into numbers.
3. **Logistic regression** uses those numbers to score the six emotions.
4. Streamlit shows the highest-scoring emotion, a bar chart, and words with positive contributions to that emotion's linear-model score. The explanation is generated locally from those weights, not by an external AI service.

The saved model loads once, on the first prediction, and is reused. Input and the latest 10 results remain in the current session's memory; the app does not write them to a database or log. **Save result** lets you explicitly download the current result to your computer. Session counters cover all successful analyses since the last reset, including those no longer in the recent list.

## Main files

| File | Purpose |
|---|---|
| `app.py` | Streamlit page |
| `styles.css` | Small local stylesheet for the dashboard |
| `emotion_model.py` | Input checks and prediction |
| `model/emotion_model.pkl.gz` | Small, already-trained model |
| `train_model.py` | Optional training and evaluation |
| `data/` | Compressed English training/test data and attribution |
| `requirements.txt` | Two direct dependencies: Streamlit and scikit-learn |
| `tests/test_project.py` | Model and interface checks |

The app has no Flask server, transformer models, translation, external AI API, retrieval system, database, batch uploads, or separate frontend build.

## Results and limits

The model trained on 16,000 examples from the [DAIR-AI Emotion dataset](data/README.md). It achieved **88.2% accuracy** and **0.842 macro F1** on 1,989 test examples, after excluding 11 exact training duplicates. Detailed results are in [model/evaluation.json](model/evaluation.json). These results apply to this dataset and are not a guarantee for new sentences.

- This basic model supports English text. Other scripts are rejected. It does not automatically identify every language written with English letters.
- Neutral and disgust are not training labels. Factual sentences may be assigned one of the six emotions even when none fits well.
- Sarcasm, negation, unfamiliar words, and mixed feelings can be misunderstood.
- The displayed score is the model's estimate, not verified confidence. A weak or closely tied prediction shows a warning.
- This is a student demo, not a tool for diagnosing anyone's mental state.

## Check or retrain

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe train_model.py
```

Retraining is optional. It overwrites the saved model and evaluation report using the included data. Keep the pinned scikit-learn version: changing it requires retraining the saved model and rerunning the checks. Only load model files you trust.

The earlier Flask implementation and its documents were preserved outside this repository before simplification. Old reports describe the previous system and its measurements; use this README for the current app.
