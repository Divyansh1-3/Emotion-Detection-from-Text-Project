"""Analysis API Blueprint implementing the teacher's exact API contract.

Endpoints:
- POST /api/v1/emotion/process
- POST /api/v1/emotion/batch
- GET  /api/v1/emotion/results
- GET  /api/v1/emotion/results/<int:id>
- GET  /api/v1/emotion/stats
- GET  /health
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from backend.app.core.config import get_settings
from backend.app.engines.emotion_model import is_model_loaded as is_emotion_loaded
from backend.app.engines.sarcasm_model import is_model_loaded as is_sarcasm_loaded
from backend.app.schemas.analysis import AnalyzeRequest, BatchRequest
from backend.app.services.analysis_service import AnalysisService

analysis_bp = Blueprint("analysis_api", __name__, url_prefix="/api/v1/emotion")
health_bp = Blueprint("health_api", __name__)

_service = AnalysisService()


@analysis_bp.route("/process", methods=["POST"])
def process_text():
    """POST /api/v1/emotion/process — Analyze a single text input."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON payload"}), 400

    try:
        req = AnalyzeRequest(**data)
    except ValidationError as e:
        errs = [
            {"loc": list(err.get("loc", [])), "msg": str(err.get("msg", "")), "type": str(err.get("type", ""))}
            for err in e.errors()
        ]
        return jsonify({"success": False, "error": "Validation error", "details": errs}), 422
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


    try:
        response = _service.process_single(
            text=req.input,
            session_id=req.session_id or "",
            options=req.options,
        )
        return jsonify(response), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": "Internal pipeline error", "detail": str(ex)}), 500


@analysis_bp.route("/batch", methods=["POST"])
def process_batch():
    """POST /api/v1/emotion/batch — Analyze multiple inputs (CSV upload or JSON list)."""
    # 1. Check for file upload (CSV)
    if "file" in request.files:
        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return jsonify({"success": False, "error": "No selected file"}), 400
        content = uploaded_file.read().decode("utf-8", errors="replace")
        session_id = request.form.get("session_id", "")
        res = _service.process_batch_csv(file_content=content, session_id=session_id)
        return jsonify(res), 200

    # 2. Check for JSON body
    data = request.get_json(silent=True)
    if data:
        # Support either 'texts' or 'inputs' field
        texts = data.get("texts") or data.get("inputs") or []
        session_id = data.get("session_id", "")
        if not isinstance(texts, list):
            return jsonify({"success": False, "error": "'texts' or 'inputs' must be a list"}), 422
        res = _service.process_batch_texts(texts=texts, session_id=session_id)
        return jsonify(res), 200

    return jsonify({"success": False, "error": "Provide either a CSV file or JSON list of texts"}), 400


@analysis_bp.route("/results", methods=["GET"])
def list_results():
    """GET /api/v1/emotion/results — Paginated list of persisted analyses."""
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)
    results = _service.list_results(limit=limit, offset=offset)
    total = _service.count_results()
    return jsonify({
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": results,
    }), 200


@analysis_bp.route("/results/<int:analysis_id>", methods=["GET"])
def get_result(analysis_id: int):
    """GET /api/v1/emotion/results/<id> — Fetch a specific analysis record."""
    record = _service.get_result(analysis_id)
    if not record:
        return jsonify({"success": False, "error": f"Record with ID {analysis_id} not found"}), 404
    return jsonify({"success": True, "result": record}), 200


@analysis_bp.route("/stats", methods=["GET"])
def get_stats():
    """GET /api/v1/emotion/stats — Aggregate metrics and emotion distribution."""
    return jsonify({"success": True, "stats": _service.get_stats()}), 200


@health_bp.route("/health", methods=["GET"])
def health_check():
    """GET /health — Service health and model status."""
    settings = get_settings()
    return jsonify({
        "status": "ok",
        "service": "P_098 Emotion Detection from Text",
        "models": {
            "emotion_model": settings.emotion_model,
            "emotion_loaded": is_emotion_loaded(),
            "sarcasm_model": settings.sarcasm_model,
            "sarcasm_loaded": is_sarcasm_loaded(),
            "embedding_model": settings.embedding_model,
        },
        "llm": {
            "mode": settings.llm_mode,
            "enabled": settings.llm_enabled,
            "model": settings.openai_model,
        },
    }), 200
