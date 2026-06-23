"""Health check route."""

from fastapi import APIRouter

from phase1_cli.data import PROJECT_ENGLISH_NAME, PROJECT_NAME, PROJECT_VERSION
from phase2_api.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    return {
        "status": "ok",
        "project": PROJECT_ENGLISH_NAME,
        "display_name": PROJECT_NAME,
        "version": PROJECT_VERSION,
    }
