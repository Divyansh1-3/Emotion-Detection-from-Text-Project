"""P_098 Emotion Detection from Text - Quick Start Launcher

Usage:
    python run.py
"""
import sys
from pathlib import Path

# Add project root to Python module search path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.main import app
from backend.app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    banner = f"""
==================================================
  P_098 Emotion Detection from Text
  Candidate: Divya | HCL Industrial Training
  Interactive Dashboard : http://{settings.flask_host}:{settings.flask_port}
  Audit /inspect View   : http://{settings.flask_host}:{settings.flask_port}/inspect
  API Health Check      : http://{settings.flask_host}:{settings.flask_port}/health
==================================================
"""
    print(banner)
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.flask_env == "development",
    )
