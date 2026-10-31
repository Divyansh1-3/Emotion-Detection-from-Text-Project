"""Pretrained emotion and irony transformers. No heuristic or TF-IDF fallback."""

import math
import os
import re
import threading
from dataclasses import dataclass
from functools import lru_cache

MAX_CHARACTERS = 1000
MAX_TOKENS = 512
EMOTIONS = ("anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise")
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
EMOTION_REVISION = "0e1cd914e3d46199ed785853e12b57304e04178b"
SARCASM_MODEL = "cardiffnlp/twitter-roberta-base-irony"
SARCASM_REVISION = "3bf8f118bdf6b00c99658151ef10c9a0b9afd6bf"
SARCASM_LOW = 0.2
SARCASM_HIGH = 0.8
_model_lock = threading.RLock()
_inference_lock = threading.Lock()


class ModelUnavailableError(RuntimeError):
    """A real transformer could not be loaded or used."""


def validate_text(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter an English sentence first.")
    text = text.strip()
    if len(text) > MAX_CHARACTERS:
        raise ValueError(f"Please keep your text under {MAX_CHARACTERS + 1} characters.")
    if any(letter.isalpha() and not letter.isascii() for letter in text):
        raise ValueError("Please use English text with English letters only.")
    if not re.search(r"[A-Za-z]{2,}", text):
        raise ValueError("Please enter English words, not just numbers or symbols.")
    return text


def prepare_irony_text(text):
    """Use the TweetEval model card's URL and username preprocessing."""
    return " ".join(
        "@user" if word.startswith("@") and len(word) > 1 else
        "http" if word.startswith("http") else word
        for word in text.split()
    )


def checked_scores(scores, expected_labels):
    """Reject incompatible checkpoints and invalid inference outputs explicitly."""
    if set(scores) != set(expected_labels):
        raise ModelUnavailableError("The transformer returned an unexpected set of labels.")
    values = {str(label): float(score) for label, score in scores.items()}
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values.values()):
        raise ModelUnavailableError("The transformer returned invalid scores.")
    total = sum(values.values())
    if not math.isclose(total, 1.0, abs_tol=0.001):
        raise ModelUnavailableError("The transformer returned an invalid score distribution.")
    return {label: value / total for label, value in values.items()}


@dataclass
class TransformerClassifier:
    tokenizer: object
    model: object
    labels: tuple

    def predict(self, text):
        import torch

        encoded = self.tokenizer(text, return_tensors="pt", truncation=False)
        if encoded["input_ids"].shape[-1] > MAX_TOKENS:
            raise ValueError("This text is too long for the transformer. Please shorten it.")
        with torch.inference_mode():
            logits = self.model(**encoded).logits.float()
            if tuple(logits.shape) != (1, len(self.labels)):
                raise ModelUnavailableError("The transformer returned an unexpected output shape.")
            probabilities = logits.softmax(dim=-1)[0].tolist()
        return dict(zip(self.labels, probabilities))


@lru_cache(maxsize=2)
def _load_classifier(model_id, revision, expected_labels):
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        torch.set_num_threads(2)
        # Pinned checkpoints predate safetensors. Modern PyTorch's weights_only
        # loader is used; arbitrary repository code is never enabled.
        options = dict(revision=revision, trust_remote_code=False, token=False)
        offline = os.environ.get("HF_HUB_OFFLINE", "").lower() in {"1", "true", "yes"}
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True, **options)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_id, local_files_only=True, use_safetensors=False,
                weights_only=True, dtype=torch.float16, **options,
            )
        except OSError:
            if offline:
                raise
            tokenizer = AutoTokenizer.from_pretrained(model_id, **options)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_id, use_safetensors=False, weights_only=True, dtype=torch.float16, **options,
            )
        labels = tuple(str(model.config.id2label[i]).lower() for i in range(model.config.num_labels))
        if set(labels) != set(expected_labels):
            raise ModelUnavailableError(f"Unexpected label mapping in {model_id}.")
        model.to("cpu").eval()
        return TransformerClassifier(tokenizer, model, labels)
    except Exception as error:
        raise ModelUnavailableError(
            f"Could not load {model_id}. Install requirements.txt and allow the first model "
            "download from Hugging Face, then try Analyze again. No prediction was generated."
        ) from error


def load_models():
    """Serialize cold loading so concurrent sessions share one copy of each model."""
    with _model_lock:
        emotion = _load_classifier(EMOTION_MODEL, EMOTION_REVISION, EMOTIONS)
        sarcasm = _load_classifier(SARCASM_MODEL, SARCASM_REVISION, ("non_irony", "irony"))
    return emotion, sarcasm


def sarcasm_result(score):
    # The broad uncertain band is a display policy, not measured calibration.
    uncertain = SARCASM_LOW < score < SARCASM_HIGH
    detected = score >= SARCASM_HIGH
    return {
        "score": score,
        "detected": detected,
        "uncertain": uncertain,
        "label": "Uncertain" if uncertain else "Likely sarcasm" if detected else "Sarcasm not detected",
    }


def predict_emotion(text):
    """Return separate transformer scores for emotion and sarcasm/irony."""
    text = validate_text(text)
    emotion_model, sarcasm_model = load_models()
    try:
        # Bound simultaneous activation memory on small CPU hosts. Only model
        # objects are shared across users; input/result data is never cached.
        with _inference_lock:
            scores = checked_scores(emotion_model.predict(text), EMOTIONS)
            irony_scores = checked_scores(sarcasm_model.predict(prepare_irony_text(text)), ("non_irony", "irony"))
    except (ValueError, ModelUnavailableError):
        raise
    except Exception as error:
        raise ModelUnavailableError("Transformer inference failed. Please try again; no result was saved.") from error
    ranked = sorted(scores, key=scores.get, reverse=True)
    best, second = ranked[:2]
    return {
        "emotion": best,
        "score": scores[best],
        "scores": scores,
        "uncertain": scores[best] < 0.45 or scores[best] - scores[second] < 0.10,
        "runner_up": second,
        "sarcasm": sarcasm_result(irony_scores["irony"]),
        "backend": "pretrained_transformers",
        "models": {"emotion": EMOTION_MODEL, "sarcasm": SARCASM_MODEL},
        "revisions": {"emotion": EMOTION_REVISION, "sarcasm": SARCASM_REVISION},
    }
