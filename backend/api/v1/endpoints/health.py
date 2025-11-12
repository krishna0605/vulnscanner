from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.session import get_async_session

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/db/health")
async def db_health(session: AsyncSession = Depends(get_async_session)):
    """Check connectivity to the database and return basic info."""
    q = text(
        """
        SELECT version() AS version,
               current_database() AS db,
               inet_server_port() AS port
        """
    )
    result = await session.execute(q)
    row = result.mappings().first() or {}
    return {"ok": True, "info": {"version": row.get("version"), "db": row.get("db"), "port": row.get("port")}}