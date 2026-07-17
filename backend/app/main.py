from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.dependencies import DatabaseSession
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.routers.users import router as users_router

app = FastAPI(
    title="Fitness Application API",
    description="An API for managing fitness routines and tracking progress.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profile_router)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """检查 API 进程是否正常运行。"""

    return {"status": "ok"}


@app.get("/health/database", tags=["system"])
def database_health_check(
    database_session: DatabaseSession,
) -> dict[str, str]:
    """检查 API 是否能够连接 PostgreSQL。"""

    database_session.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }
