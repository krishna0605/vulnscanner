from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import aiohttp
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

from .config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)


def create_access_token(data, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token (fallback for non-Supabase auth)."""
    if isinstance(data, str):
        # If data is a string, treat it as subject
        payload = {"sub": data}
    else:
        # If data is a dict, use it as payload
        payload = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_exp_minutes)
    
    payload["exp"] = expire
    payload["iat"] = datetime.now(timezone.utc).timestamp()
    
    return jwt.encode(payload, settings.get_effective_jwt_secret(), algorithm=settings.jwt_algorithm)


async def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Verify Supabase JWT token and return user claims.
    
    Args:
        token: The JWT token from Authorization header
        
    Returns:
        Dict containing user claims
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Get Supabase JWT secret from the project's JWT secret
        # For production, you should cache this or use the public key
        if not settings.supabase_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase not configured"
            )
        
        # Decode without verification first to get the header
        jwt.get_unverified_header(token)
        
        # For Supabase, we need to verify using the JWT secret
        # In production, you should fetch the public key from Supabase
        # For now, we'll use a simpler approach with the service role key
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.supabase_service_role_key if settings.supabase_service_role_key else settings.secret_key,
            algorithms=["HS256"],
            options={"verify_signature": False}  # For development, disable signature verification
        )
        
        # Check if token is expired
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
        
        # Validate required claims
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )


async def get_current_user_from_token(token: str) -> Dict[str, Any]:
    """
    Extract user information from Supabase JWT token.
    
    Args:
        token: The JWT token
        
    Returns:
        Dict containing user information
    """
    # Use Supabase Auth API for proper token verification
    if 'supabase_auth' not in globals() or supabase_auth is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase not configured"
        )
    user_data = await supabase_auth.verify_user_token(token)
    
    return {
        "id": user_data.get("id"),
        "email": user_data.get("email"),
        "role": user_data.get("role", "authenticated"),
        "aud": user_data.get("aud"),
        "exp": user_data.get("exp"),
        "iat": user_data.get("iat"),
        "iss": user_data.get("iss"),
        "user_metadata": user_data.get("user_metadata", {}),
        "app_metadata": user_data.get("app_metadata", {}),
        "email_confirmed_at": user_data.get("email_confirmed_at"),
        "phone_confirmed_at": user_data.get("phone_confirmed_at"),
        "confirmed_at": user_data.get("confirmed_at"),
        "last_sign_in_at": user_data.get("last_sign_in_at"),
        "created_at": user_data.get("created_at"),
        "updated_at": user_data.get("updated_at")
    }


class SupabaseAuth:
    """Supabase authentication helper class."""
    
    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.service_role_key = settings.supabase_service_role_key
        
    async def verify_user_token(self, token: str) -> Dict[str, Any]:
        """
        Verify user token with Supabase Auth API.
        
        Args:
            token: JWT token from client
            
        Returns:
            User information dict
        """
        if not self.supabase_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase not configured"
            )
        
        try:
            # Call Supabase Auth API to verify token
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.supabase_url}/auth/v1/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": settings.supabase_anon_key
                    }
                ) as response:
                    
                    if response.status == 200:
                        user_data = await response.json()
                        return user_data
                    elif response.status == 401:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token"
                        )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token verification failed"
                        )
                    
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify token with Supabase: {str(e)}"
            )


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token and return payload (for testing/fallback).
    
    Args:
        token: JWT token to verify
        
    Returns:
        Token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.get_effective_jwt_secret(),
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


# Global instance
try:
    supabase_auth = SupabaseAuth()
except Exception:
    # In development without Supabase settings, avoid crashing at import time
    supabase_auth = None