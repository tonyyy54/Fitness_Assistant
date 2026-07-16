from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db


app = FastAPI(
    title="Fitness Application API",
    description="An API for managing fitness routines and tracking progress.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """check if the API process is running normally."""

    return {"status": "ok"}


@app.get("/health/database", tags=["system"])
def database_health_check(
    database_session: Session = Depends(get_db),
) -> dict[str, str]:
    """check if the API can connect to PostgreSQL."""

    database_session.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }