"""Bounded batch input, independent row outcomes and spreadsheet-safe CSV export."""

import csv
import io
from dataclasses import dataclass

from emotion_model import EMOTIONS, ModelUnavailableError, predict_emotion

MAX_BATCH_ROWS = 50
MAX_BATCH_BYTES = 1024 * 1024


@dataclass(frozen=True)
class BatchInput:
    row: int
    text: str
    error: str = ""


def _check_rows(rows):
    if not rows:
        raise ValueError("Add at least one sentence to the batch.")
    if len(rows) > MAX_BATCH_ROWS:
        raise ValueError(f"Use at most {MAX_BATCH_ROWS} rows per batch.")
    return rows


def parse_lines(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Add at least one sentence to the batch.")
    if len(text.encode("utf-8")) > MAX_BATCH_BYTES:
        raise ValueError("Keep the batch input under 1 MB.")
    return _check_rows([BatchInput(i, line) for i, line in enumerate(text.splitlines(), 1)])


def parse_csv(data):
    if len(data) > MAX_BATCH_BYTES:
        raise ValueError("Keep the CSV file under 1 MB.")
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("Upload a UTF-8 CSV file with a text column.") from error
    try:
        reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
        header = next(reader, [])
        names = [name.strip().lower() for name in header]
        if names.count("text") != 1:
            raise ValueError("The CSV must have exactly one column named text.")
        text_index = names.index("text")
        rows = []
        for i, values in enumerate(reader, 1):
            if i > MAX_BATCH_ROWS:
                raise ValueError(f"Use at most {MAX_BATCH_ROWS} rows per batch.")
            value = values[text_index] if text_index < len(values) else ""
            error = "" if len(values) == len(header) else "CSV row has a different number of fields than the header."
            rows.append(BatchInput(i, value, error))
    except csv.Error as error:
        raise ValueError("The CSV is malformed. Check its quotes and column separators.") from error
    return _check_rows(rows)


def analyze_batch(rows, predictor=None):
    """Yield one outcome per input, retaining errors without fabricated predictions."""
    predictor = predictor or predict_emotion
    model_error = None
    for item in rows:
        outcome = {"row": item.row, "text": item.text, "status": "error", "error": "", "result": None}
        if item.error:
            outcome["error"] = item.error
        elif model_error:
            outcome["error"] = "Not analyzed because a model became unavailable. Retry this batch after resolving the model error."
        else:
            try:
                outcome["result"] = predictor(item.text)
                outcome["status"] = "success"
            except ValueError as error:
                outcome["error"] = str(error)
            except ModelUnavailableError as error:
                outcome["error"] = str(error)
                model_error = str(error)
        yield outcome


def _safe_cell(value):
    # CSV quoting alone does not stop spreadsheet formula evaluation.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def batch_csv(outcomes):
    fields = ["row", "text", "status", "emotion", "emotion_score", "emotion_uncertain",
              "sarcasm", "irony_score", "sarcasm_uncertain", "error",
              "emotion_model", "emotion_revision", "sarcasm_model", "sarcasm_revision",
              *["score_" + emotion for emotion in EMOTIONS]]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for item in outcomes:
        row = {key: item[key] for key in ("row", "text", "status", "error")}
        result = item["result"]
        if result is not None:
            row.update(emotion=result["emotion"], emotion_score=result["score"],
                       emotion_uncertain=result["uncertain"], sarcasm=result["sarcasm"]["label"],
                       irony_score=result["sarcasm"]["score"], sarcasm_uncertain=result["sarcasm"]["uncertain"],
                       emotion_model=result["models"]["emotion"], emotion_revision=result["revisions"]["emotion"],
                       sarcasm_model=result["models"]["sarcasm"], sarcasm_revision=result["revisions"]["sarcasm"])
            row.update({"score_" + label: result["scores"][label] for label in EMOTIONS})
        writer.writerow({key: _safe_cell(value) for key, value in row.items()})
    return buffer.getvalue().encode("utf-8-sig")


def display_rows(outcomes):
    return [{
        "Row": item["row"], "Text": item["text"], "Status": item["status"].title(),
        "Emotion": item["result"]["emotion"].title() if item["result"] else "",
        "Model score": f'{item["result"]["score"]:.1%}' if item["result"] else "",
        "Emotion uncertain": str(item["result"]["uncertain"]) if item["result"] else "",
        "Sarcasm": item["result"]["sarcasm"]["label"] if item["result"] else "",
        "Irony score": f'{item["result"]["sarcasm"]["score"]:.1%}' if item["result"] else "",
        "Error": item["error"],
    } for item in outcomes]
