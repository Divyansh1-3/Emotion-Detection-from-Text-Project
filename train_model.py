"""Optional: rebuild and evaluate the small model. The app does not run this."""

import csv
import gzip
import json
import pickle
from pathlib import Path
from time import perf_counter

import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent


def read_data(split):
    with gzip.open(ROOT / "data" / f"{split}.csv.gz", "rt", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    return [row["text"] for row in rows], [row["emotion"] for row in rows]


def main():
    train_texts, train_labels = read_data("train")
    test_texts, test_labels = read_data("test")
    # Keep test sentences that are not exact duplicates of training sentences.
    seen = {" ".join(text.lower().split()) for text in train_texts}
    test_pairs = [(text, label) for text, label in zip(test_texts, test_labels)
                  if " ".join(text.lower().split()) not in seen]
    clean_texts, clean_labels = zip(*test_pairs)

    model = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=12000, ngram_range=(1, 2), sublinear_tf=True)),
        ("classifier", LogisticRegression(C=3.0, class_weight="balanced", max_iter=300)),
    ])
    started = perf_counter()
    model.fit(train_texts, train_labels)
    training_seconds = perf_counter() - started
    predictions = model.predict(clean_texts)

    model_folder = ROOT / "model"
    model_folder.mkdir(exist_ok=True)
    with gzip.open(model_folder / "emotion_model.pkl.gz", "wb") as output:
        pickle.dump(model, output, protocol=5)
    report = {
        "method": "TF-IDF + logistic regression",
        "scikit_learn_version": sklearn.__version__,
        "train_examples": len(train_texts),
        "test_examples": len(clean_texts),
        "excluded_test_duplicates": len(test_texts) - len(clean_texts),
        "accuracy": accuracy_score(clean_labels, predictions),
        "macro_f1": f1_score(clean_labels, predictions, average="macro"),
        "training_seconds": round(training_seconds, 3),
        "per_emotion": classification_report(clean_labels, predictions, output_dict=True),
    }
    (model_folder / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Trained in {training_seconds:.1f}s; test accuracy: {report['accuracy']:.1%}")
    print(f"Macro F1: {report['macro_f1']:.3f}; test examples: {len(clean_texts)}")


if __name__ == "__main__":
    main()
