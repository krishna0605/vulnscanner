from fastapi import APIRouter, Depends
from typing import Dict, Any

from schemas.auth import UserPublic
from core.auth_deps import get_current_user


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> UserPublic:
    """Return the currently authenticated user's public profile."""
    return UserPublic(
        id=str(current_user.get("id")),
        email=current_user.get("email"),
        username=current_user.get("username"),
        full_name=current_user.get("full_name"),
        role=current_user.get("role"),
        is_active=current_user.get("is_active", True),
        email_verified=current_user.get("email_verified", False),
    )