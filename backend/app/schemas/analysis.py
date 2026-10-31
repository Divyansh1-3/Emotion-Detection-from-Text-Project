"""Pydantic schemas that validate/typing requests at the API boundary.

Using Pydantic (a standalone validation library — *not* part of FastAPI) with
Flask gives us the typed request/response contract the teacher guide asks for.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import AliasChoices, BaseModel, Field, field_validator

# Absolute hard cap; the per-request configured limit (MAX_INPUT_CHARS) is
# enforced in the service so it can stay env-tunable.
_HARD_MAX = 20_000


class AnalyzeRequest(BaseModel):
    """Body of POST /api/v1/emotion/process."""

    input: str = Field(..., min_length=1, max_length=_HARD_MAX)
    options: dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None

    @field_validator("input")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("input must not be empty")
        return v


class BatchRequest(BaseModel):
    """JSON body of POST /api/v1/emotion/batch (CSV upload handled in the route)."""

    texts: list[str] = Field(..., min_length=1, validation_alias=AliasChoices("texts", "inputs"))
    session_id: Optional[str] = None

    @field_validator("texts")
    @classmethod
    def _clean(cls, v: list[str]) -> list[str]:
        # Keep row positions, including blanks, so errors identify the original row.
        return v
