# Historical English emotion dataset

These compressed files were used for the earlier TF-IDF baseline. The current
pretrained transformer dashboard does not train on or load them. Its small
regression set is documented in [regression/README.md](regression/README.md).

Source: [DAIR-AI Emotion on Hugging Face](https://huggingface.co/datasets/dair-ai/emotion), `split` configuration.

- `train.csv.gz`: 16,000 labelled English examples, used for training.
- `test.csv.gz`: 2,000 examples, used only for evaluation.
- Columns: `text`, `emotion`.
- Labels: anger, fear, joy, love, sadness, surprise.
- `source.json` records the exact upstream revision, URLs, and original file hashes.

The upstream Parquet files were converted to compressed CSV without changing their texts or labels. The historical training script reads them with Python's standard library. The current app downloads pretrained transformer weights on first use instead.

The dataset was automatically labelled and may contain errors, informal language, and offensive text. Its test score measures performance on this dataset, not every kind of English writing. Exact training duplicates are excluded from test scoring by `train_model.py`.

The dataset authors specify **educational and research use only**. This project is an educational demo. See the [upstream usage terms](https://github.com/dair-ai/emotion_dataset#usage).

Citation: Elvis Saravia, Hsien-Chi Toby Liu, Yen-Hao Huang, Junlin Wu, and Yi-Shin Chen. 2018. [CARER: Contextualized Affect Representations for Emotion Recognition](https://aclanthology.org/D18-1404/). Proceedings of EMNLP, pages 3687–3697.
