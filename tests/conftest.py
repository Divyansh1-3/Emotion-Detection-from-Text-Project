"""Pytest configuration and test environment setup.

Ensures tests run deterministically, fast, and offline without requiring
external network downloads or live API keys.
"""
from __future__ import annotations

import os
import tempfile
import atexit
from pathlib import Path

# Disable heavy model downloads during test suite execution
os.environ["USE_MODELS"] = "0"
os.environ["LLM_MODE"] = "mock"
_test_dir = tempfile.TemporaryDirectory(prefix="p098_tests_")
atexit.register(_test_dir.cleanup)
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_test_dir.name) / "test.sqlite3")
os.environ["OPENAI_API_KEY"] = ""
os.environ["HF_HUB_OFFLINE"] = "1"
