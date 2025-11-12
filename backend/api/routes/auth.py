from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from core.auth_deps import get_current_user, get_user_id
from core.supabase import is_supabase_configured, get_supabase_client
from services.auth_service import auth_service
from schemas.auth import UserCreate, UserLogin, Token, LoginResponse, UserPublic, PasswordReset, EmailVerification, RefreshTokenRequest


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/dev-test")
async def dev_test():
    """Test endpoint to check development mode."""
    from core.config import settings
    return {
        "development_mode": settings.development_mode,
        "skip_supabase": settings.skip_supabase,
        "message": "Development test endpoint"
    }


@router.post("/register", response_model=UserPublic)
async def register(data: UserCreate):
    """
    Register a new user.
    
    This endpoint creates a new user account. In development mode,
    it uses the local SQLite database. In production, it uses Supabase Auth.
    """
    try:
        result = await auth_service.register_user(data)
        print(f"Registration result: {result}")
        user, access_token = result
        return user
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Registration exception: {type(e).__name__}: {str(e)}")
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(data: UserLogin):
    """
    Login user with email and password.
    
    This endpoint authenticates a user and returns a JWT token
    that can be used for subsequent API requests.
    """
    try:
        token_data = await auth_service.login_user(data)
        return token_data
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        if "invalid" in str(e).lower() or "credentials" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout(user_id: str = Depends(get_user_id)):
    """
    Logout current user.
    
    This endpoint invalidates the user's session and access token.
    """
    try:
        client = get_supabase_client()
        if client:
            client.auth.sign_out()
        
        return {"message": "Successfully logged out"}
        
    except Exception:
        # Even if logout fails, we can return success since the client
        # should discard the token anyway
        return {"message": "Logged out"}


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information.
    
    This endpoint returns the profile information of the currently authenticated user.
    """
    return UserPublic(
        id=str(current_user["id"]),
        email=current_user.get("email", ""),
        full_name=current_user.get("full_name", ""),
        email_confirmed=current_user.get("email_confirmed", True)
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    This endpoint generates a new access token using a valid refresh token.
    """
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        return Token(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/forgot-password")
async def forgot_password(data: PasswordReset):
    """
    Send password reset email.
    
    This endpoint sends a password reset email to the user's email address.
    """
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )
    
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable"
            )
        
        # Send password reset email
        _ = client.auth.reset_password_email(data.email)
        
        # Always return success for security reasons (don't reveal if email exists)
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception:
        # Always return success for security reasons
        return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/verify-email")
async def verify_email(data: EmailVerification):
    """
    Verify email address with token.
    
    This endpoint verifies a user's email address using the verification token
    sent to their email.
    """
    try:
        result = await auth_service.verify_email(data.email, data.token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email verification failed: {str(e)}"
        )


@router.post("/resend-verification")
async def resend_verification_email(email: str):
    """
    Resend email verification.
    
    This endpoint resends the email verification link to the user's email address.
    """
    if not is_supabase_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured"
        )
    
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable"
            )
        
        # Resend verification email
        _ = client.auth.resend({"type": "signup", "email": email})
        
        return {"message": "Verification email sent"}
        
    except Exception:
        # Return success for security reasons
        return {"message": "If the email exists, a verification email has been sent"}


@router.get("/health")
async def auth_health_check():
    """
    Check authentication service health.
    
    This endpoint checks if the authentication service (Supabase) is available
    and properly configured.
    """
    from core.supabase import test_supabase_connection
    
    connection_status = await test_supabase_connection()
    
    return {
        "status": "healthy" if connection_status["connection_test"] else "unhealthy",
        "supabase_configured": connection_status["configured"],
        "client_available": connection_status["client_available"],
        "admin_client_available": connection_status["admin_client_available"],
        "connection_test": connection_status["connection_test"],
        "error": connection_status.get("error")
    }