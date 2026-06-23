"""Pydantic schemas for the Phase 2 API."""

from typing import Any

from pydantic import BaseModel, Field


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


class GameStateResponse(BaseModel):
    game_id: str
    state: dict[str, Any]


class ActionRequest(BaseModel):
    text: str = Field(min_length=1)


class ActionResponse(BaseModel):
    game_id: str
    response: dict[str, Any]
