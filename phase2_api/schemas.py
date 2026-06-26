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


class OriginListResponse(BaseModel):
    countries: list[dict[str, Any]]
    backgrounds: list[dict[str, Any]]


class CharacterCreateRequest(BaseModel):
    name: str = Field(default="无名冒险者", min_length=1)
    class_id: str
    god: str


class CharacterResponse(BaseModel):
    character: dict[str, Any]


class GameCreateRequest(CharacterCreateRequest):
    game_mode: str = Field(default="tutorial")
    origin_country_id: str | None = None
    origin_city: str | None = None
    origin_ethnicity: str | None = None
    background_id: str | None = None


class GameCreateResponse(BaseModel):
    game_id: str
    state: dict[str, Any]
    opening_text: str
    game_mode: str
    setup: dict[str, Any]


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


class GameEvent(BaseModel):
    event_index: int
    text: str


class GameEventsResponse(BaseModel):
    game_id: str
    events: list[GameEvent]


class GameDeleteResponse(BaseModel):
    game_id: str
    deleted: bool


class ActionRequest(BaseModel):
    text: str = Field(min_length=1)
    include_debug: bool = False


class ActionResponse(BaseModel):
    game_id: str
    response: dict[str, Any]
    story: str
    state: dict[str, Any]
    mechanics: dict[str, Any]
    debug: dict[str, Any] | None = None
