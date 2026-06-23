"""FastAPI entry point for Pantheon Age Phase 2."""

from fastapi import FastAPI

from phase1_cli.data import PROJECT_ENGLISH_NAME, PROJECT_NAME, PROJECT_VERSION
from phase2_api.routes import characters, classes, games, health, locations


app = FastAPI(
    title=f"{PROJECT_NAME} / {PROJECT_ENGLISH_NAME}",
    version=PROJECT_VERSION,
    description="Rule-driven text adventure API for Pantheon Age.",
)

app.include_router(health.router)
app.include_router(classes.router)
app.include_router(locations.router)
app.include_router(characters.router)
app.include_router(games.router)
