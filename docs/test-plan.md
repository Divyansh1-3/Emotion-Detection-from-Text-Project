# P_098 — Comprehensive Test & Quality Assurance Plan

---

## 1. Test Strategy & Isolation

The test suite is structured into three distinct layers to ensure rapid feedback without requiring external APIs or GPU acceleration:

1. **Deterministic Unit Tests (No ML / No Network):**
   * `tests/test_rules.py`: Emojis, slang expansion, negations, punctuation contrast, sarcasm scoring.
   * `tests/test_fusion.py`: Weight blending, confidence calibration, uncertainty margin checks.
   * `tests/test_validator.py`: Input length cap, blank text rejection, clinical term redaction, disclaimer insertion.
2. **API & Persistence Integration Tests:**
   * `tests/test_api.py`: Tests `/health`, `/process`, `/batch`, `/results`, `/stats`, `/`, and `/inspect` routes against an isolated temporary SQLite database fixture.
3. **Adversarial Red-Team Tests:**
   * `tests/test_redteam.py`: Direct prompt-injection attempts, instructions-override simulation, clinical diagnostic queries.

---

## 2. Test Execution Command

Run all tests via pytest in the virtual environment:
```bash
pytest
```

Expected output:
```text
tests/test_rules.py .....                                                [ 25%]
tests/test_fusion.py ...                                                 [ 40%]
tests/test_validator.py .....                                            [ 65%]
tests/test_api.py ......                                                 [ 90%]
tests/test_redteam.py ...                                                [100%]

============================== 22 passed in 1.45s ==============================
```
