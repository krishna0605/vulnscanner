"""
Authentication dependencies for FastAPI (local-only JWT).

This module provides dependency functions for authenticating users
and extracting user information from JWT tokens.
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import auth_service
from .config import settings


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    
    This dependency extracts and validates the JWT token from the
    Authorization header and returns user information.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        # Verify token using auth service
        payload = await auth_service.verify_token(credentials.credentials)
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Get user information
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Return user information in expected format
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user from JWT token (optional).
    
    This dependency is similar to get_current_user but doesn't raise
    an error if no token is provided. Useful for endpoints that work
    with both authenticated and anonymous users.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        Dict containing user information or None if not authenticated
    """
    if not credentials:
        return None
    
    try:
        # Verify token using auth service
        payload = await auth_service.verify_token(credentials.credentials)
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get user information
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            return None
        
        # Return user information in expected format
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
        
    except Exception:
        return None


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current active user (additional validation).
    
    This dependency adds additional validation to ensure the user
    is active and has the required permissions.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        Dict containing active user information
        
    Raises:
        HTTPException: If user is inactive or doesn't have required permissions
    """
    # Check if user is active (you can add more validation here)
    if current_user.get("role") == "banned":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned"
        )
    
    # Add any additional validation logic here
    # For example, check subscription status, email verification, etc.
    
    return current_user


async def require_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require admin user role.
    
    This dependency ensures that only users with admin role
    can access the protected endpoint.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        Dict containing admin user information
        
    Raises:
        HTTPException: If user is not an admin
    """
    user_role = current_user.get("role", "user")
    
    if user_role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Extract user ID from current user.
    
    Convenience dependency that returns just the user ID.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        User ID as string (UUID format)
    """
    
    user_id = current_user.get("id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )
    
    return str(user_id)


# Supabase webhook verification removed; local-only auth enforced


class UserPermissions:
    """Helper class for checking user permissions."""
    
    @staticmethod
    def can_access_project(user: Dict[str, Any], project_owner_id: str) -> bool:
        """
        Check if user can access a specific project.
        
        Args:
            user: User information dict
            project_owner_id: ID of the project owner
            
        Returns:
            True if user can access the project
        """
        user_id = user.get("id")
        user_role = user.get("role", "user")
        
        # Admin users can access all projects
        if user_role in ["admin", "super_admin"]:
            return True
        
        # Users can access their own projects
        if user_id == project_owner_id:
            return True
        
        # TODO: Add logic for shared projects/team members
        # This would involve checking project_members table
        
        return False
    
    @staticmethod
    def can_modify_project(user: Dict[str, Any], project_owner_id: str) -> bool:
        """
        Check if user can modify a specific project.
        
        Args:
            user: User information dict
            project_owner_id: ID of the project owner
            
        Returns:
            True if user can modify the project
        """
        user_id = user.get("id")
        user_role = user.get("role", "user")
        
        # Admin users can modify all projects
        if user_role in ["admin", "super_admin"]:
            return True
        
        # Users can modify their own projects
        if user_id == project_owner_id:
            return True
        
        # TODO: Add logic for project collaborators with edit permissions
        
        return False


# Global permissions instance
permissions = UserPermissions()