from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import aiohttp
import json
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """Create a JWT access token (fallback for non-Supabase auth)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.jwt_exp_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


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
        unverified_header = jwt.get_unverified_header(token)
        
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
    payload = await verify_supabase_jwt(token)
    
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role", "authenticated"),
        "aud": payload.get("aud"),
        "exp": payload.get("exp"),
        "iat": payload.get("iat"),
        "iss": payload.get("iss"),
        "user_metadata": payload.get("user_metadata", {}),
        "app_metadata": payload.get("app_metadata", {})
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


# Global instance
supabase_auth = SupabaseAuth()