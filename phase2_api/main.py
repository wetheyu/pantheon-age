"""FastAPI entry point for Pantheon Age Phase 2."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from phase1_cli.data import PROJECT_ENGLISH_NAME, PROJECT_NAME, PROJECT_VERSION
from phase2_api.routes import characters, classes, games, gods, health, locations, origins


def cors_origins_from_env():
    raw_origins = os.getenv(
        "PANTHEON_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(
    title=f"{PROJECT_NAME} / {PROJECT_ENGLISH_NAME}",
    version=PROJECT_VERSION,
    description="Rule-driven text adventure API for Pantheon Age.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_from_env(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(classes.router)
app.include_router(gods.router)
app.include_router(locations.router)
app.include_router(origins.router)
app.include_router(characters.router)
app.include_router(games.router)
