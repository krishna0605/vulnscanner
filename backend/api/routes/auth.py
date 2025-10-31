from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional

from core.supabase import get_supabase_client, get_supabase_admin_client, is_supabase_configured
from core.auth_deps import get_current_user, get_current_user_optional, get_user_id
from core.security import supabase_auth
from schemas.auth import UserCreate, UserLogin, Token, UserPublic, PasswordReset, EmailVerification


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
async def register(data: UserCreate):
    """
    Register a new user with Supabase Auth.
    
    This endpoint creates a new user account using Supabase authentication.
    The user will receive an email verification link if email confirmation is enabled.
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
        
        # Register user with Supabase
        response = client.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.full_name
                }
            }
        })
        
        if response.user:
            return UserPublic(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name", ""),
                email_confirmed=response.user.email_confirmed_at is not None
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
            
    except Exception as e:
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    """
    Login user with email and password.
    
    This endpoint authenticates a user with Supabase and returns a JWT token
    that can be used for subsequent API requests.
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
        
        # Authenticate with Supabase
        response = client.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        if response.session and response.session.access_token:
            return Token(
                access_token=response.session.access_token,
                token_type="bearer",
                expires_in=response.session.expires_in,
                refresh_token=response.session.refresh_token
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
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
        
    except Exception as e:
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
        id=current_user["id"],
        email=current_user.get("email", ""),
        full_name=current_user.get("user_metadata", {}).get("full_name", ""),
        email_confirmed=current_user.get("email_confirmed_at") is not None
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    
    This endpoint generates a new access token using a valid refresh token.
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
        
        # Refresh the session
        response = client.auth.refresh_session(refresh_token)
        
        if response.session and response.session.access_token:
            return Token(
                access_token=response.session.access_token,
                token_type="bearer",
                expires_in=response.session.expires_in,
                refresh_token=response.session.refresh_token
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
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
        response = client.auth.reset_password_email(data.email)
        
        # Always return success for security reasons (don't reveal if email exists)
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        # Always return success for security reasons
        return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/verify-email")
async def verify_email(data: EmailVerification):
    """
    Verify email address with token.
    
    This endpoint verifies a user's email address using the verification token
    sent to their email.
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
        
        # Verify email with token
        response = client.auth.verify_otp({
            "email": data.email,
            "token": data.token,
            "type": "email"
        })
        
        if response.user:
            return {"message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
        response = client.auth.resend({"type": "signup", "email": email})
        
        return {"message": "Verification email sent"}
        
    except Exception as e:
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