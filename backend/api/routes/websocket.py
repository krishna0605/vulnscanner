"""WebSocket endpoints for real-time dashboard updates.
Provides live data streaming for scan progress, metrics, and notifications.
Enhanced with comprehensive authentication and session management.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.supabase import get_supabase_client
from db.session import async_session
from models import Project, ScanSession
from schemas.dashboard import ScanProgressUpdate, DashboardMetricUpdate, RealTimeUpdate
from api.middleware.auth import auth_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Enhanced WebSocket connection manager with authentication integration."""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store project subscriptions by user_id -> set of project_ids
        self.project_subscriptions: Dict[str, Set[str]] = {}
        # Store scan subscriptions by user_id -> set of scan_ids
        self.scan_subscriptions: Dict[str, Set[str]] = {}
        # Store user permissions cache
        self.user_permissions: Dict[str, Dict[str, bool]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, user_data: Dict):
        """Accept a new WebSocket connection with authentication."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
            self.project_subscriptions[user_id] = set()
            self.scan_subscriptions[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        
        # Cache user permissions
        session = await auth_manager.get_session(user_id)
        if session:
            self.user_permissions[user_id] = session.get("permissions", {})
        
        logger.info(f"WebSocket connected for user {user_id} with permissions: {self.user_permissions.get(user_id, {})}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.project_subscriptions:
                    del self.project_subscriptions[user_id]
                if user_id in self.scan_subscriptions:
                    del self.scan_subscriptions[user_id]
                if user_id in self.user_permissions:
                    del self.user_permissions[user_id]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections for a specific user."""
        if user_id in self.active_connections:
            disconnected = set()
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                    # Update session activity
                    await auth_manager.update_session_activity(user_id)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(websocket)
            
            # Remove disconnected websockets
            for websocket in disconnected:
                self.active_connections[user_id].discard(websocket)
    
    async def subscribe_to_project(self, user_id: str, project_id: str) -> bool:
        """Subscribe user to project updates with permission check."""
        # Check if user has realtime access permission
        permissions = self.user_permissions.get(user_id, {})
        if not permissions.get("realtime_access", False):
            return False
        
        if user_id in self.project_subscriptions:
            self.project_subscriptions[user_id].add(project_id)
            logger.info(f"User {user_id} subscribed to project {project_id}")
            return True
        return False
    
    async def unsubscribe_from_project(self, user_id: str, project_id: str):
        """Unsubscribe user from project updates."""
        if user_id in self.project_subscriptions:
            self.project_subscriptions[user_id].discard(project_id)
            logger.info(f"User {user_id} unsubscribed from project {project_id}")
    
    async def subscribe_to_scan(self, user_id: str, scan_id: str) -> bool:
        """Subscribe user to scan updates with permission check."""
        # Check if user has realtime access permission
        permissions = self.user_permissions.get(user_id, {})
        if not permissions.get("realtime_access", False):
            return False
        
        if user_id in self.scan_subscriptions:
            self.scan_subscriptions[user_id].add(scan_id)
            logger.info(f"User {user_id} subscribed to scan {scan_id}")
            return True
        return False
    
    async def unsubscribe_from_scan(self, user_id: str, scan_id: str):
        """Unsubscribe user from scan updates."""
        if user_id in self.scan_subscriptions:
            self.scan_subscriptions[user_id].discard(scan_id)
            logger.info(f"User {user_id} unsubscribed from scan {scan_id}")
    
    async def broadcast_project_update(self, project_id: str, update: dict):
        """Broadcast update to all users subscribed to a project."""
        sent_count = 0
        for user_id, project_ids in self.project_subscriptions.items():
            if project_id in project_ids:
                await self.send_personal_message(update, user_id)
                sent_count += 1
        logger.debug(f"Broadcasted project {project_id} update to {sent_count} users")
    
    async def broadcast_scan_update(self, scan_id: str, update: dict):
        """Broadcast update to all users subscribed to a scan."""
        sent_count = 0
        for user_id, scan_ids in self.scan_subscriptions.items():
            if scan_id in scan_ids:
                await self.send_personal_message(update, user_id)
                sent_count += 1
        logger.debug(f"Broadcasted scan {scan_id} update to {sent_count} users")
    
    async def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics."""
        return {
            "active_connections": sum(len(connections) for connections in self.active_connections.values()),
            "unique_users": len(self.active_connections),
            "project_subscriptions": sum(len(projects) for projects in self.project_subscriptions.values()),
            "scan_subscriptions": sum(len(scans) for scans in self.scan_subscriptions.values())
        }


# Global connection manager instance
manager = ConnectionManager()


async def verify_websocket_auth(websocket: WebSocket) -> Dict:
    """Enhanced WebSocket authentication using the auth manager."""
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            raise HTTPException(status_code=401, detail="Missing token")
        
        # Use the enhanced authentication manager
        user_data = await auth_manager.authenticate_websocket(websocket, token)
        return user_data
        
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        raise


@router.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    """Enhanced WebSocket endpoint for dashboard real-time updates."""
    user_id = None
    user_data = None
    
    try:
        # Verify authentication with enhanced system
        user_data = await verify_websocket_auth(websocket)
        user_id = user_data["id"]
        
        # Connect to manager with user data
        await manager.connect(websocket, user_id, user_data)
        
        # Send initial connection confirmation with session info
        session = await auth_manager.get_session(user_id)
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "permissions": session.get("permissions", {}) if session else {},
            "session_id": session.get("created_at") if session else None
        }))
        
        # Send connection statistics if user is admin
        if session and session.get("permissions", {}).get("dashboard_admin", False):
            stats = await manager.get_connection_stats()
            await websocket.send_text(json.dumps({
                "type": "admin_stats",
                "data": stats
            }))
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(websocket, user_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if user_id:
            manager.disconnect(websocket, user_id)
            # Disconnect from auth manager as well
            await auth_manager.disconnect_websocket(user_id)


async def handle_websocket_message(websocket: WebSocket, user_id: str, message: dict):
    """Enhanced WebSocket message handling with permission checks."""
    message_type = message.get("type")
    
    # Update session activity
    await auth_manager.update_session_activity(user_id)
    
    if message_type == "subscribe_project":
        project_id = message.get("project_id")
        if not project_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "project_id is required"
            }))
            return
        
        # Verify user owns the project or has admin access
        async with async_session() as db:
            query = select(Project).where(Project.id == project_id)
            result = await db.execute(query)
            project = result.scalar_one_or_none()
            
            if not project:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Project not found"
                }))
                return
            
            # Check access permissions
            session = await auth_manager.get_session(user_id)
            has_admin = session and session.get("permissions", {}).get("dashboard_admin", False)
            owns_project = project.owner_id == user_id
            
            if not (owns_project or has_admin):
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Access denied to this project"
                }))
                return
            
            # Subscribe with permission check
            success = await manager.subscribe_to_project(user_id, project_id)
            if success:
                await websocket.send_text(json.dumps({
                    "type": "subscription",
                    "status": "subscribed",
                    "project_id": project_id,
                    "project_name": project.name
                }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Subscription failed - insufficient permissions"
                }))
    
    elif message_type == "unsubscribe_project":
        project_id = message.get("project_id")
        if project_id:
            await manager.unsubscribe_from_project(user_id, project_id)
            await websocket.send_text(json.dumps({
                "type": "subscription",
                "status": "unsubscribed",
                "project_id": project_id
            }))
    
    elif message_type == "subscribe_scan":
        scan_id = message.get("scan_id")
        if not scan_id:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "scan_id is required"
            }))
            return
        
        # Verify user owns the scan or has admin access
        async with async_session() as db:
            query = (
                select(ScanSession)
                .join(Project)
                .where(ScanSession.id == scan_id)
            )
            result = await db.execute(query)
            scan = result.scalar_one_or_none()
            
            if not scan:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Scan not found"
                }))
                return
            
            # Check access permissions
            session = await auth_manager.get_session(user_id)
            has_admin = session and session.get("permissions", {}).get("dashboard_admin", False)
            owns_scan = scan.project.owner_id == user_id
            
            if not (owns_scan or has_admin):
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Access denied to this scan"
                }))
                return
            
            # Subscribe with permission check
            success = await manager.subscribe_to_scan(user_id, scan_id)
            if success:
                await websocket.send_text(json.dumps({
                    "type": "subscription",
                    "status": "subscribed",
                    "scan_id": scan_id,
                    "scan_status": scan.status
                }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Subscription failed - insufficient permissions"
                }))
    
    elif message_type == "unsubscribe_scan":
        scan_id = message.get("scan_id")
        if scan_id:
            await manager.unsubscribe_from_scan(user_id, scan_id)
            await websocket.send_text(json.dumps({
                "type": "subscription",
                "status": "unsubscribed",
                "scan_id": scan_id
            }))
    
    elif message_type == "get_session_info":
        # Send current session information
        session = await auth_manager.get_session(user_id)
        if session:
            await websocket.send_text(json.dumps({
                "type": "session_info",
                "data": {
                    "user_id": user_id,
                    "permissions": session.get("permissions", {}),
                    "last_activity": session.get("last_activity"),
                    "websocket_connected": session.get("websocket_connected", False)
                }
            }))
    
    elif message_type == "get_connection_stats":
        # Only allow admin users to get connection stats
        session = await auth_manager.get_session(user_id)
        if session and session.get("permissions", {}).get("dashboard_admin", False):
            stats = await manager.get_connection_stats()
            active_users = await auth_manager.get_active_users()
            await websocket.send_text(json.dumps({
                "type": "connection_stats",
                "data": {
                    **stats,
                    "active_users": active_users
                }
            }))
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Admin permission required"
            }))
    
    elif message_type == "ping":
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": message.get("timestamp"),
            "server_time": json.dumps(datetime.now(timezone.utc), default=str)
        }))
    
    else:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }))


# Functions to be called by background tasks for broadcasting updates
async def broadcast_scan_progress(scan_id: str, progress_data: ScanProgressUpdate):
    """Broadcast scan progress update to subscribed users."""
    update = {
        "type": "scan_progress",
        "scan_id": scan_id,
        "data": progress_data.model_dump()
    }
    await manager.broadcast_scan_update(scan_id, update)


async def broadcast_dashboard_metric(user_id: str, metric_data: DashboardMetricUpdate):
    """Broadcast dashboard metric update to a specific user."""
    update = {
        "type": "dashboard_metric",
        "data": metric_data.model_dump()
    }
    await manager.send_personal_message(update, user_id)


async def broadcast_realtime_update(update: RealtimeUpdate):
    """Broadcast general realtime update."""
    message = {
        "type": "realtime_update",
        "data": update.model_dump()
    }
    
    # Determine which users to send to based on update type
    if update.entity_type == "scan" and update.entity_id:
        await manager.broadcast_scan_update(update.entity_id, message)
    elif update.entity_type == "project" and update.entity_id:
        await manager.broadcast_project_update(update.entity_id, message)


# Export the manager for use in other modules
__all__ = ["manager", "broadcast_scan_progress", "broadcast_dashboard_metric", "broadcast_realtime_update"]