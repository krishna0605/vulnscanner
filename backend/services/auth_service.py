"""
Authentication service for handling JWT tokens and user management.

This service provides a unified interface for authentication that works with
both Supabase and local development environments.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple

from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy import select

from core.security import verify_password as core_verify_password, get_password_hash as core_get_password_hash

from core.config import settings
# Supabase integration removed; using local database and JWT only
from db.session import get_db, async_session
from models.unified_models import Profile
from schemas.auth import UserCreate, UserLogin, UserPublic

logger = logging.getLogger(__name__)

# Password hashing using bcrypt directly


class AuthService:
    """Authentication service for JWT token management and user operations."""
    
    def __init__(self):
        # Local-only auth: no external provider initialization
        pass
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return core_verify_password(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return core_get_password_hash(password)
    
    def create_access_token(
        self, 
        subject: str, 
        expires_minutes: Optional[int] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            subject: User ID or identifier
            expires_minutes: Token expiration in minutes
            additional_claims: Additional claims to include in token
            
        Returns:
            JWT token string
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=expires_minutes or settings.jwt_exp_minutes
        )
        
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": "vulnscanner-api",
            "aud": "vulnscanner-frontend"
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # First try to decode as our local JWT
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.jwt_algorithm],
                audience="vulnscanner-frontend",
                issuer="vulnscanner-api"
            )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
    
    async def register_user(self, user_data: UserCreate) -> Tuple[UserPublic, str]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (user_public, access_token)
            
        Raises:
            HTTPException: If registration fails
        """
        # Local-only registration
        return await self._register_local_user(user_data)
    
    async def _register_local_user(self, user_data: UserCreate) -> Tuple[UserPublic, str]:
        """Register user in local SQLite database."""
        print(f"Starting local user registration for: {user_data.email}")
        async with async_session() as db_session:
            print("Database session created successfully")
            try:
                # Check if user already exists
                query = select(Profile).where(Profile.email == user_data.email)
                result = await db_session.execute(query)
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already exists"
                    )
                
                # Generate username from email
                username = user_data.email.split('@')[0]
                
                # Hash password
                hashed_password = self.get_password_hash(user_data.password)
                
                # Create new user profile
                new_profile = Profile(
                    email=user_data.email,
                    hashed_password=hashed_password,
                    full_name=user_data.full_name or "",
                    username=username,
                    is_active=True,
                    email_confirmed=True  # Auto-confirm in dev mode
                )
                
                db_session.add(new_profile)
                await db_session.commit()
                await db_session.refresh(new_profile)
                
                # Generate access token
                access_token = self.create_access_token(
                    subject=str(new_profile.id),
                    additional_claims={"email": new_profile.email}
                )
                
                # Create UserPublic response
                user_public = UserPublic(
                    id=str(new_profile.id),
                    email=new_profile.email,
                    full_name=new_profile.full_name or "",
                    email_confirmed=new_profile.email_confirmed,
                    created_at=new_profile.created_at,
                    updated_at=new_profile.updated_at
                )
                
                return user_public, access_token
                
            except HTTPException:
                raise
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Local user registration failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Registration failed"
                )
            finally:
                await db_session.close()
    
    # Removed Supabase registration; local-only flows enforced
    
    async def authenticate_user(self, login_data: UserLogin) -> Tuple[UserPublic, str]:
        """
        Authenticate user and return user info with access token.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Tuple of (user_public, access_token)
            
        Raises:
            HTTPException: If authentication fails
        """
        # Local-only authentication
        return await self._authenticate_local_user(login_data)
    
    async def _authenticate_local_user(self, login_data: UserLogin) -> Tuple[UserPublic, str]:
        """Authenticate user against local SQLite database."""
        async for db_session in get_db():
            try:
                # Find user by email
                query = select(Profile).where(Profile.email == login_data.email)
                result = await db_session.execute(query)
                user = result.scalar_one_or_none()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )
                
                # Verify password
                if not user.hashed_password or not self.verify_password(login_data.password, user.hashed_password):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )
                
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Account is disabled"
                    )
                
                # Create access token
                access_token = self.create_access_token(
                    subject=user.id,
                    additional_claims={
                        "email": user.email,
                        "role": user.role
                    }
                )
                
                user_public = UserPublic(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    role=user.role,
                    is_active=user.is_active,
                    email_verified=user.email_confirmed,
                    created_at=user.created_at
                )
                
                return user_public, access_token
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Local user authentication failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication failed"
                )
            finally:
                await db_session.close()
    
    # Removed Supabase authentication; local-only flows enforced
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserPublic]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User information or None if not found
        """
        # Local-only user retrieval
        return await self._get_local_user_by_id(user_id)
    
    async def _get_local_user_by_id(self, user_id: str) -> Optional[UserPublic]:
        """Get user from local database."""
        async for db_session in get_db():
            try:
                query = select(Profile).where(Profile.id == user_id)
                result = await db_session.execute(query)
                user = result.scalar_one_or_none()
                
                if not user:
                    return None
                
                return UserPublic(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    role=user.role,
                    is_active=user.is_active,
                    email_verified=user.email_confirmed,
                    created_at=user.created_at
                )
                
            except Exception as e:
                logger.error(f"Failed to get local user by ID: {e}")
                return None
            finally:
                await db_session.close()
    
    # Removed Supabase user retrieval; local-only flows enforced

    async def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """
        Login user and return token response.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Dictionary with access_token, token_type, and user data
        """
        user, access_token = await self.authenticate_user(login_data)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.model_dump()
        }

    async def logout_user(self, token: str) -> Dict[str, str]:
        """
        Logout user (invalidate token).
        
        Args:
            token: JWT token to invalidate
            
        Returns:
            Success message
            
        Note:
            In a stateless JWT system, logout is typically handled client-side
            by removing the token. For enhanced security, implement token blacklisting.
        """
        # For now, just return success message
        # In production, you might want to implement token blacklisting
        return {"message": "Successfully logged out"}

    async def request_password_reset(self, email: str) -> Dict[str, str]:
        """
        Request password reset for user.
        
        Args:
            email: User's email address
            
        Returns:
            Success message
        """
        if settings.development_mode or settings.skip_supabase:
            # In development mode, just return success
            # In production, you would send an actual email
            logger.info(f"Password reset requested for {email} (dev mode)")
            return {"message": "Password reset email sent"}
        else:
            # Use Supabase password reset
            try:
                if self.supabase_client:
                    self.supabase_client.auth.reset_password_email(email)
                return {"message": "Password reset email sent"}
            except Exception as e:
                logger.error(f"Password reset request failed: {e}")
                # Don't reveal if email exists for security
                return {"message": "Password reset email sent"}

    async def confirm_password_reset(self, token: str, new_password: str) -> Dict[str, str]:
        """
        Confirm password reset with token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            Success message
        """
        if settings.development_mode or settings.skip_supabase:
            # In development mode, just return success
            # In production, you would validate the token and update password
            logger.info(f"Password reset confirmed with token {token[:10]}... (dev mode)")
            return {"message": "Password reset successful"}
        else:
            # Use Supabase password reset confirmation
            try:
                if self.supabase_client:
                    # Note: Supabase handles this through their auth flow
                    # This would typically be handled by their SDK
                    pass
                return {"message": "Password reset successful"}
            except Exception as e:
                logger.error(f"Password reset confirmation failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )

    async def verify_email(self, email: str, token: str) -> Dict[str, str]:
        """
        Verify user email with token.
        
        Args:
            email: User's email address
            token: Email verification token
            
        Returns:
            Success message
        """
        if settings.development_mode or settings.skip_supabase:
            # In development mode, just return success
            logger.info(f"Email verified for {email} with token {token[:10]}... (dev mode)")
            return {"message": "Email verified successfully"}
        else:
            # Use Supabase email verification
            try:
                if self.supabase_client:
                    response = self.supabase_client.auth.verify_otp({
                        "email": email,
                        "token": token,
                        "type": "email"
                    })
                    
                    if response.user:
                        return {"message": "Email verified successfully"}
                    else:
                        raise ValueError("Invalid verification token")
                else:
                    raise ValueError("Authentication service unavailable")
            except Exception as e:
                logger.error(f"Email verification failed: {str(e)}")
                raise ValueError(f"Email verification failed: {str(e)}")
                
            return {"message": "Email verified successfully"}

    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dictionary with new access token and token type
            
        Raises:
            HTTPException: If refresh fails
        """
        if settings.development_mode or settings.skip_supabase:
            # In development mode, return mock tokens
            logger.info("Refreshing token (dev mode)")
            return {
                "access_token": "new-mock-access-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "new-mock-refresh-token"
            }
        else:
            # Use Supabase token refresh
            try:
                if not self.supabase_client:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Authentication service unavailable"
                    )
                
                response = self.supabase_client.auth.refresh_session(refresh_token)
                
                if response.session and response.session.access_token:
                    return {
                        "access_token": response.session.access_token,
                        "token_type": "bearer",
                        "expires_in": response.session.expires_in,
                        "refresh_token": response.session.refresh_token
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid refresh token"
                    )
                    
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token refresh failed: {str(e)}"
                )


# Global auth service instance
auth_service = AuthService()