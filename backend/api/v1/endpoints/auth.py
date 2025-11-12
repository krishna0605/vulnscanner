from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from schemas.auth import UserCreate, UserLogin, LoginResponse, AuthResponse
from services.auth_service import auth_service


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=LoginResponse, status_code=201)
async def signup(user: UserCreate) -> LoginResponse:
    """Register a new user using local-only authentication."""
    user_public, token = await auth_service.register_user(user)
    return LoginResponse(access_token=token, token_type="bearer", user=user_public)

# Alias for frontend expectations
@router.post("/register", response_model=LoginResponse, status_code=201)
async def register(user: UserCreate) -> LoginResponse:
    """Alias route for user registration (same as /signup)."""
    user_public, token = await auth_service.register_user(user)
    return LoginResponse(access_token=token, token_type="bearer", user=user_public)


@router.post("/login", response_model=LoginResponse)
async def login(login: UserLogin) -> LoginResponse:
    """Login with email and password; returns JWT and user info."""
    user_public, token = await auth_service.authenticate_user(login)
    return LoginResponse(access_token=token, token_type="bearer", user=user_public)


@router.post("/logout", response_model=AuthResponse)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthResponse:
    """Logout the current user by invalidating the provided JWT (stateless)."""
    await auth_service.logout_user(credentials.credentials)
    return AuthResponse(message="Successfully logged out", success=True)