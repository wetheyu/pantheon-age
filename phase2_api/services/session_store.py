"""In-memory game session store for Phase 2.

This is intentionally simple. A later phase can replace it with a repository
backed by PostgreSQL without changing the route shape.
"""

from uuid import uuid4

from fastapi import HTTPException

from phase1_cli.character import build_character
from phase1_cli.data import CLASSES, GODS
from phase1_cli.game_service import handle_player_input
from phase1_cli.game_state import GameState
from phase1_cli.story import render_opening


_SESSIONS: dict[str, GameState] = {}


def validate_character_input(class_id, god):
    if class_id not in CLASSES:
        raise HTTPException(status_code=400, detail=f"Unknown class_id: {class_id}")

    if god not in GODS:
        raise HTTPException(status_code=400, detail=f"Unknown god: {god}")


def build_api_character(name, class_id, god):
    validate_character_input(class_id, god)
    return build_character(name.strip() or "无名冒险者", class_id, god)


def create_game_session(name, class_id, god):
    character = build_api_character(name, class_id, god)
    state = GameState(character)
    game_id = uuid4().hex
    _SESSIONS[game_id] = state
    return game_id, state, render_opening(character)


def get_game_state(game_id):
    try:
        return _SESSIONS[game_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Game not found: {game_id}") from exc


def submit_game_action(game_id, text):
    state = get_game_state(game_id)
    return handle_player_input(state, text)


def clear_sessions():
    """Clear in-memory sessions for tests."""
    _SESSIONS.clear()
