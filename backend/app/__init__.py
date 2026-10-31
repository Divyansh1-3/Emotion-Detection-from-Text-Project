"""Flask Application Factory.

Configures template and static folders targeting frontend/, registers API blueprints,
sets up JSON error handlers, and initializes the persistence database.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask, jsonify

from backend.app.core.config import ROOT, get_settings
from backend.app.core.logging import configure_logging
from backend.app.repositories.results_repository import ResultsRepository
from dataclasses import replace


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application instance."""
    template_dir = ROOT / "frontend" / "templates"
    static_dir = ROOT / "frontend" / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
        static_url_path="/static",
    )

    settings = get_settings()

    # Core configuration
    app.config["JSON_SORT_KEYS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max for batch uploads

    if test_config:
        app.config.update(test_config)

    storage = replace(settings, database_url=app.config.get("DATABASE_URL", settings.database_url))
    app.extensions["results_repository"] = ResultsRepository(storage.sqlite_path)
    if not app.testing:
        configure_logging(settings.logs_dir)

    # Ensure required directories exist
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.kb_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    # Register blueprints
    from backend.app.api.routes.analysis import analysis_bp, health_bp
    from backend.app.api.routes.views import views_bp

    app.register_blueprint(analysis_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(views_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"success": False, "error": "Upload exceeds the 16 MB request limit"}), 413

    return app
