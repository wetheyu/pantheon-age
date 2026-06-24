"""Configuration helpers for Phase 3 persistence."""

import os
from pathlib import Path


DEFAULT_DB_PATH = Path("data/pantheon_age.sqlite3")
DB_PATH_ENV_VAR = "PANTHEON_DB_PATH"


def get_database_path():
    configured_path = os.environ.get(DB_PATH_ENV_VAR)
    if configured_path:
        return Path(configured_path)
    return DEFAULT_DB_PATH
