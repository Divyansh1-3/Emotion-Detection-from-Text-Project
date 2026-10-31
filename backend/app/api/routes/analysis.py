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

import csv
import io

from flask import Blueprint, Response, current_app, jsonify, request
from pydantic import ValidationError

from backend.app.core.config import get_settings
from backend.app.engines.emotion_model import is_model_loaded as is_emotion_loaded
from backend.app.engines.sarcasm_model import is_model_loaded as is_sarcasm_loaded
from backend.app.engines.retrieval import retrieval_backend
from backend.app.engines.calibration import calibration_profile
from backend.app.schemas.analysis import AnalyzeRequest, BatchRequest
from backend.app.services.analysis_service import AnalysisService

analysis_bp = Blueprint("analysis_api", __name__, url_prefix="/api/v1/emotion")
health_bp = Blueprint("health_api", __name__)

_service = AnalysisService()


@analysis_bp.route("/process", methods=["POST"])
def process_text():
    """POST /api/v1/emotion/process — Analyze a single text input."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
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
    except Exception:
        current_app.logger.exception("Single analysis failed")
        return jsonify({"success": False, "error": "Internal pipeline error"}), 500


@analysis_bp.route("/batch", methods=["POST"])
def process_batch():
    """POST /api/v1/emotion/batch — Analyze multiple inputs (CSV upload or JSON list)."""
    try:
        if "file" in request.files:
            uploaded = request.files["file"]
            if not uploaded.filename or not uploaded.filename.lower().endswith(".csv"):
                raise ValueError("Select a CSV file.")
            content = uploaded.read().decode("utf-8-sig")
            result = _service.process_batch_csv(content, request.form.get("session_id", ""))
        else:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                raise ValueError("Provide a JSON object with a 'texts' list or upload a CSV file.")
            payload = BatchRequest.model_validate(data)
            result = _service.process_batch_texts(payload.texts, payload.session_id or "")
        return jsonify(result), 200
    except ValidationError as exc:
        details = [{"loc": list(e["loc"]), "msg": e["msg"]} for e in exc.errors()]
        return jsonify(success=False, error="Invalid batch input", details=details), 422
    except UnicodeDecodeError:
        return jsonify(success=False, error="CSV must use UTF-8 encoding"), 400
    except ValueError as exc:
        return jsonify(success=False, error=str(exc)), 400


@analysis_bp.route("/results", methods=["GET"])
def list_results():
    """GET /api/v1/emotion/results — Paginated list of persisted analyses."""
    limit = max(1, min(request.args.get("limit", default=50, type=int), 500))
    offset = max(0, request.args.get("offset", default=0, type=int))
    results = _service.list_results(limit=limit, offset=offset)
    total = _service.count_results()
    return jsonify({
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": results,
    }), 200


@analysis_bp.route("/export", methods=["GET"])
def export_results():
    """Download stored results as CSV; neutralize spreadsheet formula cells."""
    stream = io.StringIO(newline="")
    columns = ["id", "request_id", "input_text", "primary_emotion", "confidence", "uncertain", "sarcasm", "rationale", "created_at", "confidence_method"]
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    for record in _service.iter_export():
        row = {key: record.get(key, "") for key in columns}
        for key, value in row.items():
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                row[key] = "'" + value
        writer.writerow(row)
    return Response(stream.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=emotion-results.csv"})


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
    profile, calibration_status = calibration_profile()
    return jsonify({
        "status": "ok",
        "service": "P_098 Emotion Detection from Text",
        "models": {
            "emotion_model": settings.emotion_model,
            "emotion_loaded": is_emotion_loaded(),
            "sarcasm_model": settings.sarcasm_model,
            "sarcasm_loaded": is_sarcasm_loaded(),
            "embedding_model": settings.embedding_model,
            "retrieval_backend": retrieval_backend(),
        },
        "degraded": not (is_emotion_loaded() and is_sarcasm_loaded() and retrieval_backend() == "embeddings"),
        "confidence_calibration": {"status": calibration_status,
                                   "scope": "English with both classifiers and embedding retrieval",
                                   "temperature": profile["temperature"] if profile else None},
        "llm": {
            "mode": settings.llm_mode,
            "enabled": settings.llm_enabled,
            "model": settings.openai_model,
        },
    }), 200
