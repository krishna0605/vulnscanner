from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.supabase import get_supabase_client
from db.session import async_session
from schemas.auth import TokenPayload
from api.middleware.auth import (
    auth_manager,
    get_current_user_with_session,
    get_current_user_optional_with_session,
    require_permission
)

security = HTTPBearer()


async def get_db() -> AsyncSession:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_legacy(token: str | None = None) -> TokenPayload | None:
    """Legacy JWT authentication - kept for backward compatibility."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# Enhanced authentication dependencies using the new middleware
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Enhanced authentication with session management.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        dict: User information with session data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    return await get_current_user_with_session(credentials)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Optionally validate JWT token and return current user information with session management.
    Returns None if no token provided or token is invalid.
    
    Args:
        credentials: Optional Bearer token from Authorization header
        
    Returns:
        dict or None: User information with session data or None
    """
    return await get_current_user_optional_with_session(credentials)


# Enhanced permission-based dependencies
def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin role using session-based permissions.
    
    Args:
        current_user: Current authenticated user with session data
        
    Returns:
        dict: User information if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    return require_permission("dashboard_admin")(current_user)


async def require_dashboard_read(current_user: dict = Depends(get_current_user)) -> dict:
    """Require dashboard read permission."""
    session = await auth_manager.get_session(current_user["id"])
    if not session or not session.get("permissions", {}).get("dashboard_read", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dashboard read permission required"
        )
    return current_user


async def require_dashboard_write(current_user: dict = Depends(get_current_user)) -> dict:
    """Require dashboard write permission."""
    session = await auth_manager.get_session(current_user["id"])
    if not session or not session.get("permissions", {}).get("dashboard_write", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dashboard write permission required"
        )
    return current_user


async def require_realtime_access(current_user: dict = Depends(get_current_user)) -> dict:
    """Require real-time access permission."""
    session = await auth_manager.get_session(current_user["id"])
    if not session or not session.get("permissions", {}).get("realtime_access", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Real-time access permission required"
        )
    return current_user


def require_project_access(project_owner_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require access to a specific project.
    
    Args:
        project_owner_id: ID of the project owner
        current_user: Current authenticated user with session data
        
    Returns:
        dict: User information if access granted
        
    Raises:
        HTTPException: If user doesn't have access to the project
    """
    user_id = current_user.get("id")
    
    # Check if user has admin permission
    session = auth_manager.get_session(user_id)
    if session and session.get("permissions", {}).get("dashboard_admin", False):
        return current_user
    
    # Allow access if user owns the project
    if user_id != project_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this project"
        )
    
    return current_user


async def csrf_protect(csrf_token: str | None = Header(default=None, alias=settings.csrf_header_name)):
    """CSRF protection middleware."""
    # If csrf_secret is set, enforce header value matches
    if not settings.csrf_secret:
        return
    if csrf_token != settings.csrf_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token invalid")