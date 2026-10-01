"""Application entrypoint for running the Flask development server or CLI.

Usage:
    python -m backend.app.main
    flask --app backend.app.main run --port 5000
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is on sys.path when executed directly
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import create_app
from backend.app.core.config import get_settings

app = create_app()

if __name__ == "__main__":
    from backend.app.engines.warmup import warm_up_models
    warm_up_models()
    settings = get_settings()
    print(f"Starting P_098 Emotion Detection server on http://{settings.flask_host}:{settings.flask_port}")
    print(f"Server-rendered inspection view available at http://{settings.flask_host}:{settings.flask_port}/inspect")
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=False,
    )
