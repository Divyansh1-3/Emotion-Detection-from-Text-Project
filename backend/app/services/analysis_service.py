"""Analysis Service: pipeline orchestration, persistence, batch processing, and logging.

This service acts as the central coordinator between the HTTP API, the hybrid
engine pipeline, and the persistence repository.
"""
from __future__ import annotations

import csv
import io
from typing import Any, Optional

from backend.app.core.config import get_settings
from backend.app.core.logging import emit_request_log
from backend.app.domain.emotion_schema import AnalysisResult
from backend.app.engines.router import execute_pipeline
from backend.app.repositories.results_repository import ResultsRepository

_repo: Optional[ResultsRepository] = None


def get_repository() -> ResultsRepository:
    global _repo
    if _repo is None:
        settings = get_settings()
        _repo = ResultsRepository(settings.sqlite_path)
    return _repo


class AnalysisService:
    def __init__(self, repo: ResultsRepository | None = None):
        self.repo = repo or get_repository()

    def process_single(
        self,
        text: str,
        session_id: str = "",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute pipeline for a single text, persist result, and return API response."""
        result: AnalysisResult = execute_pipeline(
            raw_text=text,
            session_id=session_id,
            mode="single",
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
        if len(texts) > settings.max_batch_rows:
            texts = texts[: settings.max_batch_rows]

        results = []
        for text in texts:
            if not text or not text.strip():
                continue
            try:
                item_res = self.process_single(text=text, session_id=session_id)
                results.append(item_res["result"])
            except Exception as e:
                results.append({
                    "input_text": text,
                    "error": str(e),
                    "primary_emotion": "neutral",
                    "confidence": 0.0,
                    "uncertain": True,
                    "sarcasm": False,
                })

        return {
            "success": True,
            "total_processed": len(results),
            "results": results,
        }

    def process_batch_csv(self, file_content: str, session_id: str = "") -> dict[str, Any]:
        """Parse uploaded CSV and analyze the text column."""
        reader = csv.reader(io.StringIO(file_content))
        rows = list(reader)
        if not rows:
            return {"success": False, "error": "CSV file is empty"}

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

        data_rows = rows[1:] if has_header else rows
        texts = [r[text_col] for r in data_rows if len(r) > text_col and r[text_col].strip()]

        return self.process_batch_texts(texts=texts, session_id=session_id)

    def get_result(self, analysis_id: int) -> Optional[dict[str, Any]]:
        return self.repo.get(analysis_id)

    def list_results(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        return self.repo.list(limit=limit, offset=offset)

    def count_results(self) -> int:
        return self.repo.count()

    def get_stats(self) -> dict[str, Any]:
        return self.repo.stats()
