from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.supabase import test_supabase_connection
from db.session import init_db
from api.routes.local_auth import router as auth_router
from api.routes.payments import router as payments_router
from api.routes.dashboard import router as dashboard_router
from api.routes.websocket import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (DDL may be restricted on Supabase)
    try:
        # Ensure models are imported so metadata is populated
        import models  # noqa: F401
        
        # Test Supabase connection
        await test_supabase_connection()
        
        # Initialize database
        await init_db()
        
    except Exception as e:
        # Skip auto-DDL if not permitted, but log the error
        print(f"Database initialization warning: {e}")
        pass
    yield


app = FastAPI(
    title=settings.app_name,
    description="Enhanced Vulnerability Scanner API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(dashboard_router)
app.include_router(websocket_router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    try:
        # Test Supabase connection
        await test_supabase_connection()
        return {
            "status": "ok",
            "database": "connected",
            "supabase": "connected"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "error",
            "supabase": "error",
            "error": str(e)
        }