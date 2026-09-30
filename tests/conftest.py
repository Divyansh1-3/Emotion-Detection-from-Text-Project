"""Pytest configuration and test environment setup.

Ensures tests run deterministically, fast, and offline without requiring
external network downloads or live API keys.
"""
from __future__ import annotations

import os

# Disable heavy model downloads during test suite execution
os.environ["USE_MODELS"] = "0"
os.environ["LLM_MODE"] = "mock"
os.environ["DATABASE_URL"] = "sqlite:///test_emotion.sqlite3"
