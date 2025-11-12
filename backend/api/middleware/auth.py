"""
Authentication middleware for real-time dashboard system.
Provides comprehensive user session management and security measures.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status, WebSocket, WebSocketException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import logging
from datetime import datetime, timezone

from core.config import settings
from core.supabase import get_supabase_client
from schemas.auth import TokenPayload

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Manages authentication for both HTTP and WebSocket connections."""
    
    def __init__(self):
        self.security = HTTPBearer()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
    
    async def authenticate_user(self, token: str) -> Dict[str, Any]:
        """
        Authenticate user with JWT token and return user information.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: User information with session data
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # First try to decode as local JWT token
            try:
                payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
                token_data = TokenPayload(**payload)
                
                user_data = {
                    "id": token_data.sub,
                    "email": None,  # Would need to fetch from database
                    "user_metadata": {},
                    "app_metadata": {},
                    "created_at": None,
                    "updated_at": None,
                    "auth_provider": "legacy"
                }
                await self._create_session(user_data)
                return user_data
            except JWTError:
                # If local JWT fails, try Supabase authentication
                supabase = get_supabase_client()
                if supabase:
                    try:
                        user_response = supabase.auth.get_user(token)
                        if user_response and user_response.user:
                            user = user_response.user
                            user_data = {
                                "id": user.id,
                                "email": user.email,
                                "user_metadata": user.user_metadata or {},
                                "app_metadata": user.app_metadata or {},
                                "created_at": user.created_at,
                                "updated_at": user.updated_at,
                                "auth_provider": "supabase"
                            }
                            await self._create_session(user_data)
                            return user_data
                    except Exception as e:
                        logger.error(f"Supabase authentication failed: {e}", exc_info=True)
                        pass  # Continue to raise authentication error
                
                # If both fail, raise authentication error
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_websocket(self, websocket: WebSocket, token: str) -> Dict[str, Any]:
        """
        Authenticate WebSocket connection with JWT token.
        
        Args:
            websocket: WebSocket connection
            token: JWT token string
            
        Returns:
            dict: User information
            
        Raises:
            WebSocketException: If authentication fails
        """
        try:
            user_data = await self.authenticate_user(token)
            
            # Register WebSocket connection
            user_id = user_data["id"]
            self.websocket_connections[user_id] = websocket
            
            # Update session with WebSocket info
            if user_id in self.active_sessions:
                self.active_sessions[user_id]["websocket_connected"] = True
                self.active_sessions[user_id]["websocket_connected_at"] = datetime.now(timezone.utc).isoformat()
            
            return user_data
            
        except HTTPException as e:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=e.detail)
        except Exception as e:
            raise WebSocketException(code=status.WS_1011_INTERNAL_ERROR, reason=f"Authentication failed: {str(e)}")
    
    async def _create_session(self, user_data: Dict[str, Any]) -> None:
        """Create or update user session."""
        user_id = user_data["id"]
        session_data = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "websocket_connected": False,
            "websocket_connected_at": None,
            "permissions": await self._get_user_permissions(user_data),
            "session_metadata": {}
        }
        self.active_sessions[user_id] = session_data
    
    async def _get_user_permissions(self, user_data: Dict[str, Any]) -> Dict[str, bool]:
        """Get user permissions based on user data."""
        # Default permissions for dashboard access
        permissions = {
            "dashboard_read": True,
            "dashboard_write": True,
            "dashboard_admin": False,
            "realtime_access": True
        }
        
        # Check for admin role in metadata
        app_metadata = user_data.get("app_metadata", {})
        user_metadata = user_data.get("user_metadata", {})
        
        if app_metadata.get("role") == "admin" or user_metadata.get("role") == "admin":
            permissions["dashboard_admin"] = True
        
        return permissions
    
    async def update_session_activity(self, user_id: str) -> None:
        """Update last activity timestamp for user session."""
        if user_id in self.active_sessions:
            self.active_sessions[user_id]["last_activity"] = datetime.now(timezone.utc).isoformat()
    
    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data."""
        return self.active_sessions.get(user_id)
    
    async def remove_session(self, user_id: str) -> None:
        """Remove user session and WebSocket connection."""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
        
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]
    
    async def disconnect_websocket(self, user_id: str) -> None:
        """Disconnect WebSocket for user."""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]
        
        if user_id in self.active_sessions:
            self.active_sessions[user_id]["websocket_connected"] = False
    
    async def get_active_users(self) -> list[Dict[str, Any]]:
        """Get list of active users."""
        return [
            {
                "user_id": session["user_id"],
                "email": session["user_data"].get("email"),
                "last_activity": session["last_activity"],
                "websocket_connected": session["websocket_connected"]
            }
            for session in self.active_sessions.values()
        ]
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific user via WebSocket."""
        if user_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[user_id]
                await websocket.send_json(message)
                return True
            except Exception:
                # Remove disconnected WebSocket
                await self.disconnect_websocket(user_id)
                return False
        return False
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> int:
        """Broadcast message to all connected users."""
        sent_count = 0
        disconnected_users = []
        
        for user_id, websocket in self.websocket_connections.items():
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception:
                disconnected_users.append(user_id)
        
        # Clean up disconnected WebSockets
        for user_id in disconnected_users:
            await self.disconnect_websocket(user_id)
        
        return sent_count
    
    async def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions."""
        current_time = datetime.now(timezone.utc)
        expired_users = []
        
        for user_id, session in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session["last_activity"].replace('Z', '+00:00'))
            age_hours = (current_time - last_activity).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            await self.remove_session(user_id)
        
        return len(expired_users)


# Global authentication manager instance
auth_manager = AuthenticationManager()


async def get_current_user_with_session(
    credentials: HTTPAuthorizationCredentials
) -> Dict[str, Any]:
    """
    Dependency to get current user with session management.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        dict: User information with session data
    """
    user_data = await auth_manager.authenticate_user(credentials.credentials)
    await auth_manager.update_session_activity(user_data["id"])
    return user_data


async def get_current_user_optional_with_session(
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user with session management.
    
    Args:
        credentials: Optional Bearer token from Authorization header
        
    Returns:
        dict or None: User information with session data or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user_with_session(credentials)
    except HTTPException:
        return None


def require_permission(permission: str):
    """
    Decorator to require specific permission for endpoint access.
    
    Args:
        permission: Required permission name
        
    Returns:
        Dependency function
    """
    async def permission_dependency(
        user: Dict[str, Any] = Depends(get_current_user_with_session)
    ) -> Dict[str, Any]:
        session = await auth_manager.get_session(user["id"])
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found"
            )
        
        permissions = session.get("permissions", {})
        if not permissions.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return user
    
    return permission_dependency