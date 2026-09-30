# P_098 — System Limitations & Failure Modes

Understanding failure boundaries is critical for deploying NLP in high-stakes environments.

---

## 1. Known Failure Modes

### 1.1 Deadpan / Implicit Sarcasm
* *Limitation:* The sarcasm model and rule cues rely heavily on lexical incongruity (e.g. positive adjectives with negative situations) or punctuation markers (`!`, `...`, caps).
* *Failure Case:* "I really enjoy sitting in morning traffic." Without exclamation marks or known negative context, the system may classify this literally as `joy`.
* *Mitigation:* Sarcasm is exposed as a probability score with explicit warnings; the uncertainty badge flags low-margin cases.

### 1.2 Code-Switching & Non-Standard Dialects
* *Limitation:* The pretrained DistilRoBERTa model was primarily trained on standard English text and GoEmotions Reddit corpora.
* *Failure Case:* Heavy regional slang, multilingual code-switching (e.g., Hinglish, Spanglish), or obscure acronyms may degrade classification accuracy.
* *Mitigation:* The `preprocess.py` engine translates common internet slang, and `langdetect` flags non-English input text.

### 1.3 Extremely Brief Utterances
* *Limitation:* Inputs consisting of single words or ambiguous particles (e.g., "Right.", "Fine.", "Well...") lack sufficient semantic context.
* *Failure Case:* High probability of being classified as `neutral` with low confidence.
* *Mitigation:* The system triggers the `uncertain` flag when confidence is $< 0.40$, alerting operators.

---

## 2. Safety & Ethical Boundaries

1. **Non-Clinical Guarantee:** P_098 does not assess mental health, depression, suicidal ideation, or personality disorders.
2. **Deterministic Bias:** Pretrained transformer models inherit societal biases present in public social media corpora.
3. **No Autonomous Clinical Action:** Outputs must never be used to make automated psychiatric decisions or deny critical services.
