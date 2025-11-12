from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from core.config import settings
from db.session import engine, async_session
from models.unified_models import Base
# Import routers
from api.routes.auth import router as auth_router
from api.routes.health import router as health_router
from api.v1.endpoints.health import router as v1_health_router
from api.v1.endpoints.auth import router as v1_auth_router
from api.v1.endpoints.users import router as v1_users_router
from api.routes.payments import router as payments_router
from api.routes.dashboard import router as dashboard_router
from api.routes.websocket import router as websocket_router
from api.routes.scan_results import router as scan_results_router
from api.routes.projects import router as projects_router
from api.routes.scans import router as scans_router
from api.v1.endpoints.scan_jobs import router as v1_scan_jobs_router
from schemas.auth import UserCreate
from services.auth_service import auth_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (DDL may be restricted on Supabase)
    try:
        # Ensure models are imported so metadata is populated
        import models  # noqa: F401
        # Database initialization via Alembic migrations executed in Docker Compose (db-init)
        # Initialize database via Alembic migrations executed in Docker Compose (db-init)
        # In development with SQLite, ensure tables exist
        if settings.is_development() and "sqlite" in str(engine.url):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Skip auto-DDL if not permitted, but log the error
        print(f"Database initialization warning: {e}")

    # Seed a development user to simplify local testing
    if settings.is_development():
        try:
            # Attempt to create dev user; ignore if already exists
            dev_user = UserCreate(email="test@example.com", password="testpassword123", full_name="Test User")
            await auth_service.register_user(dev_user)
            print("✅ Seeded development user: test@example.com")
        except Exception as e:
            # If user exists or any non-critical error, continue
            print(f"ℹ️ Dev user seed skipped: {e}")
    yield


app = FastAPI(
    title=settings.app_name,
    description="Enhanced Vulnerability Scanner API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS: allow configured origins and broaden regex in development
# If running in development, allow any http(s) origin to avoid local port mismatches
dev_allow_origin_regex = r"^https?://.*$" if settings.is_development() else r"https?://(localhost|127\.0\.0\.1)(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=dev_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(v1_health_router)
app.include_router(v1_auth_router)
app.include_router(v1_users_router)

# Dispose DB engine on shutdown to release connections
@app.on_event("shutdown")
async def _shutdown_dispose_engine():
    try:
        engine.dispose()
    except Exception as e:
        print(f"Engine dispose warning: {e}")
app.include_router(payments_router)
app.include_router(dashboard_router)
app.include_router(websocket_router)
app.include_router(scan_results_router)
app.include_router(projects_router)
app.include_router(scans_router)
app.include_router(v1_scan_jobs_router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    try:
        # Test database connectivity
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "error",
            "error": str(e)
        }