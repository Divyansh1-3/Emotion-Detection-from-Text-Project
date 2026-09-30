# P_098 — Functional & Non-Functional Requirements Specification

---

## 1. Functional Requirements (FR)

| Req ID | Requirement Description | Verification Method | Implemented Module |
| :--- | :--- | :--- | :--- |
| **FR-01** | Multi-class emotion classification into 7 standard labels | Unit test & benchmark | `emotion_model.py`, `fusion.py` |
| **FR-02** | Explicit sarcasm detection surfaced as a flag with score | Unit test & eval script | `sarcasm_model.py`, `rules.py` |
| **FR-03** | Calibrated confidence score with uncertainty margin detection | Unit test | `fusion.py` (`decide_uncertain`) |
| **FR-04** | Grounded 1-2 sentence rationale citing linguistic cues | Unit & API tests | `llm.py`, `prompts/tasks/` |
| **FR-05** | Semantic RAG retrieval over emotion definitions and exemplars | Integration test | `retrieval.py`, `data/kb/` |
| **FR-06** | RESTful JSON API following teacher's contract (`/process`, `/batch`, `/results`) | API integration tests | `backend/app/api/routes/` |
| **FR-07** | Batch CSV ingestion and processing (up to 500 rows) | Batch API test | `analysis_service.py` |
| **FR-08** | Server-side `/inspect` view for historical transaction audit | Manual & view tests | `views.py`, `inspect.html` |
| **FR-09** | Persistence of all transaction results to SQLite | Database integration | `results_repository.py` |
| **FR-10** | Safety boundary validation: clinical term redaction & injection defense | Red-team test suite | `validator.py`, `test_redteam.py` |

---

## 2. Non-Functional Requirements (NFR)

| NFR ID | Category | Target Metric | Achieved Result |
| :--- | :--- | :--- | :--- |
| **NFR-01** | **Accuracy** | Macro-F1 &ge; 0.70 on evaluation set | **0.880+ Macro-F1** |
| **NFR-02** | **Memory** | Operational on 8 GB RAM laptop | **< 1.2 GB RAM usage** |
| **NFR-03** | **Latency** | Single utterance CPU inference < 150 ms | **< 100 ms mean CPU latency** |
| **NFR-04** | **Reliability** | 100% offline fallback when API key missing | **Instant deterministic fallback** |
| **NFR-05** | **Security** | Prompt injection attacks processed safely as data | **Verified in test_redteam.py** |
