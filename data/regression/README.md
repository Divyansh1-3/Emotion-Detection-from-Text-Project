# Project regression examples

These 35 emotion and 35 sarcasm examples are the hand-written review fixtures
retained from the earlier Flask implementation. They are used for smoke evaluation,
not training, threshold tuning, or a claim of independent benchmark accuracy.
They have already been examined during development and are not a held-out test set.

Run `python evaluate_transformers.py` from the repository root to run both real
pretrained models. The report includes all predictions and the user's dry-humor
example separately, including any mistakes. The binary sarcasm metrics use the
model's raw argmax (50%); the dashboard uses a separate 20–80% uncertain band.
