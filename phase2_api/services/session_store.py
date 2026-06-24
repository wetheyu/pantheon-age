"""Game session service for the Phase 2 API.

Phase 3 persists sessions through a SQLite repository while keeping the public
API route shape unchanged.
"""

from uuid import uuid4

from fastapi import HTTPException

from phase1_cli.character import build_character
from phase1_cli.data import CLASSES, GODS
from phase1_cli.game_service import handle_player_input
from phase1_cli.game_state import GameState
from phase1_cli.story import render_opening
from phase3_persistence.errors import PersistenceError
from phase3_persistence.sqlite_repository import GameSessionRepository


_REPOSITORY = GameSessionRepository()


def configure_storage(db_path):
    """Point the session service at another SQLite database path."""
    global _REPOSITORY
    _REPOSITORY = GameSessionRepository(db_path)


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
    _save_state(game_id, state)
    return game_id, state, render_opening(character)


def summarize_game_session(game_id, state):
    player = state.player
    return {
        "game_id": game_id,
        "player_name": player.name,
        "class_id": player.class_id,
        "class_name": player.class_name,
        "god": player.god,
        "current_location": state.current_location,
        "turn": state.turn,
        "is_game_over": state.is_game_over,
    }


def list_game_sessions():
    sessions = _read_sessions()
    return [summarize_game_session(game_id, state) for game_id, state in sessions]


def get_game_state(game_id):
    state = _read_state(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")
    return state


def delete_game_session(game_id):
    if not _delete_state(game_id):
        raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")


def submit_game_action(game_id, text):
    state = get_game_state(game_id)
    response = handle_player_input(state, text)
    _save_state(game_id, state)
    return response


def list_game_events(game_id):
    events = _read_events(game_id)
    if events is None:
        raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")
    return events


def clear_sessions():
    """Clear persisted sessions for tests."""
    try:
        _REPOSITORY.clear()
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _save_state(game_id, state):
    try:
        _REPOSITORY.save(game_id, state)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _read_state(game_id):
    try:
        return _REPOSITORY.get(game_id)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _read_sessions():
    try:
        return _REPOSITORY.list()
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _delete_state(game_id):
    try:
        return _REPOSITORY.delete(game_id)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _read_events(game_id):
    try:
        return _REPOSITORY.list_events(game_id)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _persistence_http_error(error):
    return HTTPException(status_code=500, detail=f"Persistence error: {error}")
