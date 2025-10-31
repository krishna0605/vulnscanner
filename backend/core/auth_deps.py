"""
Authentication dependencies for FastAPI with Supabase integration.

This module provides dependency functions for authenticating users
and extracting user information from JWT tokens.
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .security import supabase_auth, get_current_user_from_token
from .supabase import get_supabase_client
from .config import settings


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
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
    try:
        # In development mode, allow bypassing authentication
        if settings.development_mode:
            token = credentials.credentials
            if token == "dev-bypass" or token == "test-token":
                return {
                    "id": "c4727d0f-73e1-4ff9-a3d9-8636e3597c25",  # Use real UUID from existing admin user
                    "email": "admin@vulnscan.local",
                    "role": "authenticated",
                    "user_metadata": {},
                    "app_metadata": {}
                }
        
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify token and get user info
        user_info = await get_current_user_from_token(token)
        
        if not user_info or not user_info.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token"
            )
        
        return user_info
        
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
        return await get_current_user(credentials)
    except HTTPException:
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
    user_role = current_user.get("app_metadata", {}).get("role", "user")
    
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
        User ID string
    """
    return current_user["id"]


async def verify_supabase_webhook(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """
    Verify Supabase webhook signature.
    
    This dependency verifies that the request is coming from Supabase
    by validating the webhook signature.
    
    Args:
        credentials: HTTP Bearer credentials containing webhook signature
        
    Returns:
        True if webhook is valid
        
    Raises:
        HTTPException: If webhook signature is invalid
    """
    # TODO: Implement webhook signature verification
    # This would involve checking the webhook secret and signature
    # For now, we'll just check if the token matches our service role key
    
    token = credentials.credentials
    
    # In production, you should implement proper webhook signature verification
    # For now, we'll use a simple token check
    from .config import settings
    
    if token != settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    return True


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
        user_role = user.get("app_metadata", {}).get("role", "user")
        
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
        user_role = user.get("app_metadata", {}).get("role", "user")
        
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