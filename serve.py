"""Serve the application with Waitress using the hosting platform's PORT."""
from __future__ import annotations

import os

from backend.app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    port = int(os.environ.get("PORT", settings.flask_port))
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")

    # Importing the application warms the models before accepting requests.
    from backend.app.main import app
    from waitress import serve

    print(f"Serving P_098 on 0.0.0.0:{port}", flush=True)
    serve(app, host="0.0.0.0", port=port, threads=2)


if __name__ == "__main__":
    main()
