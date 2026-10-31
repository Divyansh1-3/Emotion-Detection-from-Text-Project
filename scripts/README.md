# Project utilities

- `evaluate.py`: measure hybrid or fallback inference using the curated evaluation set.
- `download_models.py`: populate the Hugging Face model cache.
- `build_index.py`: initialize retrieval.
- `package_submission.py`: produce a source-only ZIP from Git-tracked files.
- `build_documentation.py`: rebuild report, SRS, blueprint and diagrams from current evaluation JSON. Requires `python-docx` and Pillow, in addition to project dependencies. Render and review generated documents before submission.

Older document generators now stop with migration guidance because their hardcoded claims were inaccurate. Their original implementations remain in Git history. The previously prepared presentation is a historical workspace artifact; it is not required for this submission and is not regenerated with current metrics.

- `calibrate.py --download`: fetch public GoEmotions source files into ignored `data/raw`; run without the flag to fit and validate the profile.
- `evaluate_languages.py`: record full-model outputs for curated Hindi/Hinglish demonstration phrases.
