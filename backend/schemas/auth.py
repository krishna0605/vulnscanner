from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT token payload model."""
    sub: str  # Subject (user ID)
    email: Optional[str] = None
    exp: Optional[int] = None  # Expiration timestamp
    iat: Optional[int] = None  # Issued at timestamp
    aud: Optional[str] = None  # Audience
    iss: Optional[str] = None  # Issuer


class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """Public user information model."""
    id: str  # Supabase uses UUID strings
    email: EmailStr
    full_name: Optional[str] = None
    email_confirmed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    """User profile update model."""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class PasswordReset(BaseModel):
    """Password reset request model."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    token: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")


class EmailVerification(BaseModel):
    """Email verification model."""
    email: EmailStr
    token: str


class ChangePassword(BaseModel):
    """Change password model."""
    current_password: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")


class AuthResponse(BaseModel):
    """Generic authentication response model."""
    message: str
    success: bool = True


class UserSession(BaseModel):
    """User session information model."""
    user: UserPublic
    session_id: str
    expires_at: datetime
    last_activity: datetime


class AuthHealthCheck(BaseModel):
    """Authentication service health check model."""
    status: str
    supabase_configured: bool
    client_available: bool
    admin_client_available: bool
    connection_test: bool
    error: Optional[str] = None