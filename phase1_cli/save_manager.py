"""Local JSON save/load helpers for Pantheon Age v1.1."""

import json
from pathlib import Path

from game_state import GameState


SAVE_VERSION = 1
SAVE_DIR = Path(__file__).resolve().parent.parent / "saves"
DEFAULT_SAVE_PATH = SAVE_DIR / "save.json"


def save_exists(path=DEFAULT_SAVE_PATH):
    return path.exists()


def save_game(state, path=DEFAULT_SAVE_PATH):
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "save_version": SAVE_VERSION,
        "game_state": state.to_dict(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_game(path=DEFAULT_SAVE_PATH):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return GameState.from_dict(payload["game_state"])
