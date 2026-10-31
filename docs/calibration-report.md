# Experimental emotion confidence calibration

Temperature scaling adjusts the sharpness of the fused emotion distribution without changing its leading label. Fusion weights and uncertainty thresholds remain hand-tuned. Sarcasm scores, model/retrieval fallbacks and non-English outputs are not calibrated.

The profile uses temperature **1.751161**, fitted by minimizing negative log-likelihood on 700 examples from the official GoEmotions dev split. Validation uses 350 examples from the official test split. All examples have one Ekman-mapped emotion and detected English; IDs and normalized texts are disjoint between fitting and validation. Project KB and evaluation texts are excluded. Sampling uses seed 42. Source SHA-256 hashes, class counts and example IDs are recorded in [the profile](../data/calibration/temperature.json).

| Validation measurement | Before | After |
|---|---:|---:|
| Negative log-likelihood | 1.6865 | 1.5258 |
| Multiclass Brier score | 0.7322 | 0.6950 |
| Expected calibration error, 10 bins | 0.1737 | 0.0417 |
| Label accuracy | 47.1% | 47.1% |

All three calibration measures improved. Lower calibration error means the scores better reflect observed accuracy on this sample; it does not mean higher classification accuracy. The much lower accuracy here than on the small project demo set is a significant limitation.

The upstream emotion model was trained partly on GoEmotions. Its exact subset overlap with these examples is unknown. Therefore this is experimental domain calibration, not independent evidence of generalization. Single-label filtering, English detection, Reddit-domain text, class imbalance and finite sample size further limit the results. No clinical or individual-level reliability is established.

At runtime, the profile is used only for English with both transformer classifiers and embedding retrieval. The pipeline/corpus fingerprint and model settings must match; invalid, missing or incompatible profiles fall back safely to `uncalibrated_fusion`. The API, saved record, CSV and interface expose the method for each result. `/health` reports profile availability, not eligibility of every input. `CALIBRATION_ENABLED=0` disables it. Restart after replacing the profile.

Reproduce with cached models:

```text
python scripts/calibrate.py --download
python scripts/calibrate.py
python scripts/evaluate.py --mode hybrid --check
```

The download is explicit and raw dataset text stays in ignored `data/raw/goemotions`. Do not refit on the project evaluation cases or report their results as independent validation. Refit after changing fingerprinted engine code, KB content or model settings.

References and attribution:

- Guo et al. (2017), On Calibration of Modern Neural Networks: https://proceedings.mlr.press/v70/guo17a.html
- Demszky et al. (2020), GoEmotions, Google Research: https://github.com/google-research/google-research/tree/master/goemotions
- Official data and Ekman mapping: https://raw.githubusercontent.com/google-research/google-research/master/goemotions/data/
- Upstream model training description: https://huggingface.co/j-hartmann/emotion-english-distilroberta-base
