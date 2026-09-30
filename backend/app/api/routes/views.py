"""Server-rendered UI and /inspect backend views.

Frontend <-> Backend parity:
The `/inspect` view queries the SQLite database directly, displaying the exact same
record schema as the client dashboard, allowing reviewers to verify pipeline routes,
confidence calibration, sarcasm flags, and grounding evidence from the server side.
"""
from __future__ import annotations

from flask import Blueprint, abort, render_template, request

from backend.app.core.config import get_settings
from backend.app.domain.emotion_schema import EMOTION_EMOJI, EMOTION_LABELS
from backend.app.services.analysis_service import AnalysisService

views_bp = Blueprint("views", __name__)
_service = AnalysisService()


@views_bp.route("/", methods=["GET"])
def index():
    """Client-facing interactive dashboard."""
    settings = get_settings()
    stats = _service.get_stats()
    return render_template(
        "index.html",
        labels=EMOTION_LABELS,
        emojis=EMOTION_EMOJI,
        stats=stats,
        llm_mode=settings.llm_mode,
        llm_enabled=settings.llm_enabled,
    )


@views_bp.route("/inspect", methods=["GET"])
def inspect_list():
    """Backend server-rendered inspection view showing persisted records."""
    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)
    analyses = _service.list_results(limit=limit, offset=offset)
    total = _service.count_results()
    stats = _service.get_stats()

    return render_template(
        "inspect.html",
        analyses=analyses,
        total=total,
        limit=limit,
        offset=offset,
        stats=stats,
        emojis=EMOTION_EMOJI,
    )


@views_bp.route("/inspect/<int:analysis_id>", methods=["GET"])
def inspect_detail(analysis_id: int):
    """Detailed inspection of a single analysis transaction."""
    analysis = _service.get_result(analysis_id)
    if not analysis:
        abort(404)

    return render_template(
        "inspect_detail.html",
        analysis=analysis,
        emojis=EMOTION_EMOJI,
    )
