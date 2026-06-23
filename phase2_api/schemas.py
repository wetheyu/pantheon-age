"""Pydantic schemas for the Phase 2 API."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    project: str
    display_name: str
    version: str


class ClassListResponse(BaseModel):
    classes: list[dict[str, Any]]


class GodListResponse(BaseModel):
    gods: list[str]


class LocationSummary(BaseModel):
    name: str
    description: str
    exits: list[str]


class LocationListResponse(BaseModel):
    locations: list[LocationSummary]


class CharacterCreateRequest(BaseModel):
    name: str = Field(default="无名冒险者", min_length=1)
    class_id: str
    god: str


class CharacterResponse(BaseModel):
    character: dict[str, Any]


class GameCreateRequest(CharacterCreateRequest):
    pass


class GameCreateResponse(BaseModel):
    game_id: str
    state: dict[str, Any]
    opening_text: str


class GameSessionSummary(BaseModel):
    game_id: str
    player_name: str
    class_id: str
    class_name: str
    god: str
    current_location: str
    turn: int
    is_game_over: bool


class GameListResponse(BaseModel):
    games: list[GameSessionSummary]


class GameStateResponse(BaseModel):
    game_id: str
    state: dict[str, Any]


class GameDeleteResponse(BaseModel):
    game_id: str
    deleted: bool


class ActionRequest(BaseModel):
    text: str = Field(min_length=1)


class ActionResponse(BaseModel):
    game_id: str
    response: dict[str, Any]
