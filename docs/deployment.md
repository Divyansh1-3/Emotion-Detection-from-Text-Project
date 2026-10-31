# Streamlit deployment and transformer upgrade

Public URL: https://emotion-detection-from-text-project-ncignaopdfgyjcymc264jq.streamlit.app/

The transformer implementation was published as commit `7f159b6`. Its
[GitHub Actions workflow](https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project/actions/runs/41246313817)
passed dependency installation and the contract/interface and real-model suites.
On 1 November 2026, the owner reported uploading and testing the updated public app
successfully. Independent live browser verification was unavailable. The earlier
private-window check covered the previous six-label version.

## Publish a subsequent update

1. Commit and push any new application, test, documentation or `requirements.txt` changes
   to `Divyansh1-3/Emotion-Detection-from-Text-Project`, branch `main`.
2. In [Community Cloud](https://share.streamlit.io/), open the existing app and its build logs.
   Keep main file `app.py` and Python `3.13`. No secrets or API key are required.
3. Wait for dependency installation. The requirements install Transformers and CPU-only
   PyTorch, avoiding CUDA dependencies on the Linux host.
4. Open the app and click **Analyze text**. Its first prediction downloads the two pinned
   Hugging Face checkpoints (about 827 MB of weight files) and loads them on CPU.
   Subsequent predictions reuse the models.
5. Confirm the page says **Emotion and Sarcasm Detection from Text**, with seven emotion labels.
   If it still shows six labels, the transformer revision is not running.

## Public smoke check

Use a private browser window, without the owner's signed-in session.

1. Select **Joy**, then **Analyze text**. Confirm Joy and a seven-label score chart.
   Read the sarcasm result independently: even sincere text can be flagged.
2. Select **Sarcasm** (`Great, it broke the first day...`) and analyze it.
   Confirm a **Likely sarcasm** assessment with its own irony score.
3. Select **Sincere statement** and analyze it. Confirm that it is not marked likely sarcasm.
4. Confirm both assessments appear in recent history and the **Save result** download.
5. Test blank input, **Clear text**, and **Reset session**.
6. Keep a screenshot of the actual updated dashboard. Record the deployed commit and date.
   Do not reuse the earlier app's successful check as proof of this version.

## Troubleshooting

- For local setup, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
  from the repository folder. The existing Windows Python 3.13 environment was verified
  on 1 November 2026: dependencies installed, all 22 tests passed, and real-model
  dashboard analysis, chart, history and download controls worked. Cloud installation
  does not install packages into a separate local environment.
- A model-loading error means no complete analysis was produced. Check package installation,
  Hugging Face connectivity and available memory, then retry Analyze text.
- The pinned models and tokenizers must download before offline inference works.
  Do not set `HF_HUB_OFFLINE=1` on a fresh cloud instance.
- The models use float16 weights and bounded CPU inference. Cold downloads, imports,
  initialization and cloud sleep still take time. This is no longer the 655 KiB TF-IDF app.
- If Community Cloud kills the process for memory use, inspect its logs and use a host
  with sufficient memory. Do not silently replace transformers with the old classifier.
- Never upload the local virtual environment, old ZIPs, `.env`, databases or backup directories.

For a new app, select the same repository, `main`, `app.py`, and Python 3.13 under
Advanced settings, then Deploy.

Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
