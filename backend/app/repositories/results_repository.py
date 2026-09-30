"""SQLite persistence for analyses.

Every analysis is written here so that the JSON API (`/results`), the
server-rendered `/inspect` page and the frontend all read back the *same*
records.  Uses the stdlib ``sqlite3`` (no ORM dependency); the connection is
opened per call and guarded by a lock so it is safe under Flask's threaded dev
server.  Swapping ``DATABASE_URL`` to Postgres is a documented extension point.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Optional

from backend.app.domain.emotion_schema import AnalysisResult

_SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id     TEXT,
    session_id     TEXT,
    mode           TEXT,
    input_text     TEXT NOT NULL,
    language       TEXT,
    primary_emotion TEXT,
    confidence     REAL,
    uncertain      INTEGER,
    sarcasm        INTEGER,
    sarcasm_score  REAL,
    rationale      TEXT,
    llm_used       INTEGER,
    latency_ms     REAL,
    engines_used   TEXT,   -- json array
    route          TEXT,   -- json array
    emotion_scores TEXT,   -- json array of {label, score}
    sources        TEXT,   -- json array of retrieved items
    warnings       TEXT,   -- json array
    created_at     TEXT
);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_analyses_emotion ON analyses(primary_emotion);
"""

_JSON_COLS = ("engines_used", "route", "emotion_scores", "sources", "warnings")


class ResultsRepository:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        self.init_db()

    # ---- connection / schema ------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self._connect() as conn:
            conn.executescript(_SCHEMA)

    # ---- writes -------------------------------------------------------------
    def save(self, result: AnalysisResult) -> int:
        d = result.to_dict()
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO analyses
                   (request_id, session_id, mode, input_text, language, primary_emotion,
                    confidence, uncertain, sarcasm, sarcasm_score, rationale, llm_used,
                    latency_ms, engines_used, route, emotion_scores, sources, warnings, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    d["request_id"], d["session_id"], d["mode"], d["input_text"], d["language"],
                    d["primary_emotion"], float(d["confidence"]), int(bool(d["uncertain"])),
                    int(bool(d["sarcasm"])), float(d["sarcasm_score"]), d["rationale"],
                    int(bool(d["llm_used"])), float(d["latency_ms"]),
                    json.dumps(d["engines_used"]), json.dumps(d["route"]),
                    json.dumps(d["emotion_scores"]), json.dumps(d["sources"]),
                    json.dumps(d["warnings"]), d["created_at"],
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    # ---- reads --------------------------------------------------------------
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["uncertain"] = bool(d["uncertain"])
        d["sarcasm"] = bool(d["sarcasm"])
        d["llm_used"] = bool(d["llm_used"])
        for col in _JSON_COLS:
            try:
                d[col] = json.loads(d[col]) if d[col] else []
            except (TypeError, ValueError):
                d[col] = []
        return d

    def get(self, analysis_id: int) -> Optional[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
            return self._row_to_dict(row) if row else None

    def list(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        offset = max(0, int(offset))
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM analyses ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def count(self) -> int:
        with self._lock, self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) AS n FROM analyses").fetchone()["n"])

    def stats(self) -> dict[str, Any]:
        with self._lock, self._connect() as conn:
            total = int(conn.execute("SELECT COUNT(*) AS n FROM analyses").fetchone()["n"])
            uncertain = int(conn.execute("SELECT COUNT(*) AS n FROM analyses WHERE uncertain = 1").fetchone()["n"])
            sarcastic = int(conn.execute("SELECT COUNT(*) AS n FROM analyses WHERE sarcasm = 1").fetchone()["n"])
            dist_rows = conn.execute(
                "SELECT primary_emotion AS label, COUNT(*) AS n FROM analyses GROUP BY primary_emotion"
            ).fetchall()
            avg_conf_row = conn.execute("SELECT AVG(confidence) AS c FROM analyses").fetchone()
        distribution = {r["label"]: int(r["n"]) for r in dist_rows if r["label"]}
        return {
            "total": total,
            "uncertain": uncertain,
            "sarcastic": sarcastic,
            "avg_confidence": round(float(avg_conf_row["c"]), 3) if avg_conf_row["c"] is not None else 0.0,
            "distribution": distribution,
        }

    # ---- maintenance (used by tests) ---------------------------------------
    def clear(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM analyses")
            conn.commit()
