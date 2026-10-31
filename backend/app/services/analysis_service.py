"""Analysis Service: pipeline orchestration, persistence, batch processing, and logging.

This service acts as the central coordinator between the HTTP API, the hybrid
engine pipeline, and the persistence repository.
"""
from __future__ import annotations

import csv
import io
from typing import Any, Optional

from flask import current_app, has_app_context

from backend.app.core.config import get_settings
from backend.app.core.logging import emit_request_log
from backend.app.domain.emotion_schema import AnalysisResult
from backend.app.engines.router import execute_pipeline
from backend.app.repositories.results_repository import ResultsRepository

_repo: Optional[ResultsRepository] = None


def get_repository() -> ResultsRepository:
    if has_app_context():
        return current_app.extensions["results_repository"]
    global _repo
    if _repo is None:
        settings = get_settings()
        _repo = ResultsRepository(settings.sqlite_path)
    return _repo


class AnalysisService:
    def __init__(self, repo: ResultsRepository | None = None):
        self._repo = repo

    @property
    def repo(self) -> ResultsRepository:
        return self._repo if self._repo is not None else get_repository()

    def process_single(
        self,
        text: str,
        session_id: str = "",
        options: dict[str, Any] | None = None,
        mode: str = "single",
    ) -> dict[str, Any]:
        """Execute pipeline for a single text, persist result, and return API response."""
        result: AnalysisResult = execute_pipeline(
            raw_text=text,
            session_id=session_id,
            mode=mode,
            options=options,
        )

        # Persist to database
        saved_id = self.repo.save(result)
        result.id = saved_id

        # Emit structured log
        emit_request_log(
            request_id=result.request_id,
            route=result.route,
            latency_ms=result.latency_ms,
            outcome=result.primary_emotion,
            uncertain=result.uncertain,
            sarcasm=result.sarcasm,
            confidence=result.confidence,
        )

        res_dict = result.to_dict()
        return {
            "success": True,
            "result": res_dict,
            "sources": [s if isinstance(s, dict) else s.__dict__ for s in result.sources],
            "warnings": result.warnings,
            "request_id": result.request_id,
        }

    def process_batch_texts(
        self,
        texts: list[str],
        session_id: str = "",
    ) -> dict[str, Any]:
        """Process a list of input texts."""
        settings = get_settings()
        if not isinstance(texts, list) or not texts:
            raise ValueError("Provide a non-empty list of text strings.")
        if any(not isinstance(text, str) for text in texts):
            raise ValueError("Every batch item must be a text string.")
        if len(texts) > settings.max_batch_rows:
            raise ValueError(f"Batch exceeds maximum of {settings.max_batch_rows} rows; no rows processed.")

        results = []
        for row_number, text in enumerate(texts, start=1):
            try:
                item_res = self.process_single(text=text, session_id=session_id, mode="batch")
                results.append({**item_res["result"], "row_number": row_number})
            except ValueError as e:
                results.append({
                    "row_number": row_number,
                    "input_text": text,
                    "error": str(e),
                })

        failed = sum("error" in result for result in results)
        return {
            "success": True,
            "total_processed": len(results),
            "total_succeeded": len(results) - failed,
            "total_failed": failed,
            "results": results,
        }

    def process_batch_csv(self, file_content: str, session_id: str = "") -> dict[str, Any]:
        """Parse uploaded CSV and analyze the text column."""
        reader = csv.reader(io.StringIO(file_content.lstrip("\ufeff")), strict=True)
        try:
            rows = list(reader)
        except csv.Error as exc:
            raise ValueError(f"Invalid CSV: {exc}") from exc
        if not rows or not any(any(cell.strip() for cell in row) for row in rows):
            raise ValueError("CSV file is empty")

        # Find header index for 'text' or default to column 0 / 1
        header = [h.strip().lower() for h in rows[0]]
        text_col = 0
        has_header = False

        if any(h in ("text", "sentence", "input", "utterance") for h in header):
            has_header = True
            for candidate in ("text", "sentence", "input", "utterance"):
                if candidate in header:
                    text_col = header.index(candidate)
                    break
        elif len(header) > 1 and header[0] in ("id", "index", "#"):
            text_col = 1
            has_header = True

        data_rows = rows[1:] if has_header else rows
        texts = [r[text_col] if len(r) > text_col else "" for r in data_rows]

        return self.process_batch_texts(texts=texts, session_id=session_id)

    def get_result(self, analysis_id: int) -> Optional[dict[str, Any]]:
        return self.repo.get(analysis_id)

    def list_results(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        return self.repo.list(limit=limit, offset=offset)

    def count_results(self) -> int:
        return self.repo.count()

    def get_stats(self) -> dict[str, Any]:
        return self.repo.stats()
