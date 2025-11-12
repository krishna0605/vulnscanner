from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session

router = APIRouter(prefix="/api/v1/db", tags=["db"])


@router.get("/health")
async def db_health(session: AsyncSession = Depends(get_async_session)):
    """Database health endpoint for PostgreSQL connectivity."""
    try:
        result = await session.execute(
            text(
                "SELECT version() AS version, current_database() AS db, inet_server_port() AS port;"
            )
        )
        row = result.mappings().first() or {}
        return {"ok": True, "info": {"version": row.get("version"), "db": row.get("db"), "port": row.get("port")}}
    except Exception as e:
        return {"ok": False, "error": str(e)}