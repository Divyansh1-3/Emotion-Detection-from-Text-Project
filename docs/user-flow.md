# P_098 — User Interaction Flows & System States

---

## 1. Single Utterance Analysis Flow

```
[ User Enters Text or Picks Sample ]
               │
               ▼
[ Clicks "Analyze Emotion" ]
               │
               ▼
   [ UI Shows Spinner & Route Hint ]
               │
               ▼
 [ POST /api/v1/emotion/process ]
               │
   ┌───────────┴───────────┐
   ▼                       ▼
(200 OK Response)       (Error 400 / 422)
   │                       │
   ▼                       ▼
- Render Emoji & Emotion    - Show Alert Dialog
- Render Confidence %       - Keep Input Intact
- Draw Chart.js Bar Chart
- Show Sarcasm/Uncertain Badges
- Display Grounded Rationale
- Render RAG Exemplars
- Draw Route Pills & Latency
- Enable "Copy JSON" Button
- Provide Direct Link to /inspect/<id>
```

---

## 2. Batch CSV Processing Flow

1. User switches to the "Batch CSV" tab.
2. User drags and drops a CSV file or clicks "Browse" to select `data/sample/sample_inputs.csv`.
3. UI validates the `.csv` file extension and displays file name and size.
4. User clicks "Process Batch".
5. Browser dispatches `multipart/form-data` payload to `POST /api/v1/emotion/batch`.
6. Backend parses text column, executes pipeline per row, and records all transactions in SQLite.
7. UI updates with a tabular summary: index, snippet, predicted emotion pill, confidence percentage, sarcasm status, and uncertainty status.

---

## 3. Server-Side Audit Flow (`/inspect`)

1. User or reviewer navigates to `http://127.0.0.1:5000/inspect`.
2. Flask queries SQLite database through `ResultsRepository.list()`.
3. Page displays total runs recorded, uncertainty counts, mean confidence, and a paginated table.
4. Clicking "Inspect &rarr;" opens `/inspect/<id>` for complete JSON trace inspection.
