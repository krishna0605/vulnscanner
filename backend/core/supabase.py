"""
Supabase client configuration and initialization.

This module provides Supabase client instances for database operations,
authentication, and real-time subscriptions.
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from .config import settings

logger = logging.getLogger(__name__)

# Global client instances
_supabase_client = None
_supabase_admin_client = None


@lru_cache(maxsize=1)
def get_supabase_client():
    """
    Get or create Supabase client instance with anon key.
    
    This client is used for operations that don't require elevated privileges,
    such as user authentication and RLS-protected database operations.
    
    Returns:
        Supabase client instance or None if not configured
    """
    global _supabase_client
    
    if _supabase_client is None:
        try:
            # Skip Supabase initialization if configured to do so
            if settings.skip_supabase:
                logger.info("Skipping Supabase client initialization (skip_supabase=True)")
                return None
                
            if not settings.supabase_url or not settings.supabase_anon_key:
                logger.warning("Supabase URL or anon key not configured")
                return None
            
            from supabase import create_client, Client
            
            _supabase_client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_anon_key,
                options={
                    "auth": {
                        "auto_refresh_token": True,
                        "persist_session": True,
                        "detect_session_in_url": False,
                    },
                    "db": {
                        "schema": "public",
                    },
                    "global": {
                        "headers": {
                            "X-Client-Info": "vulscan-backend",
                        },
                    },
                }
            )
            
            logger.info("Supabase client initialized successfully")
            
        except ImportError as e:
            logger.error(f"Supabase library not installed: {e}")
            _supabase_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            _supabase_client = None
    
    return _supabase_client


@lru_cache(maxsize=1)
def get_supabase_admin_client():
    """
    Get or create Supabase admin client instance with service role key.
    
    This client has elevated privileges and can bypass RLS policies.
    Use with caution and only for administrative operations.
    
    Returns:
        Supabase admin client instance or None if not configured
    """
    global _supabase_admin_client
    
    if _supabase_admin_client is None:
        try:
            # Skip Supabase initialization if configured to do so
            if settings.skip_supabase:
                logger.info("Skipping Supabase admin client initialization (skip_supabase=True)")
                return None
                
            if not settings.supabase_url or not settings.supabase_service_role_key:
                logger.warning("Supabase URL or service role key not configured")
                return None
            
            from supabase import create_client, Client
            
            _supabase_admin_client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_role_key,
                options={
                    "auth": {
                        "auto_refresh_token": False,
                        "persist_session": False,
                    },
                    "db": {
                        "schema": "public",
                    },
                    "global": {
                        "headers": {
                            "X-Client-Info": "vulscan-backend-admin",
                        },
                    },
                }
            )
            
            logger.info("Supabase admin client initialized successfully")
            
        except ImportError as e:
            logger.error(f"Supabase library not installed: {e}")
            _supabase_admin_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase admin client: {e}")
            _supabase_admin_client = None
    
    return _supabase_admin_client


def is_supabase_configured() -> bool:
    """
    Check if Supabase is properly configured.
    
    Returns:
        True if Supabase URL and keys are configured
    """
    return bool(
        settings.supabase_url and 
        settings.supabase_anon_key and 
        not settings.supabase_url.startswith("your-project")
    )


async def test_supabase_connection() -> Dict[str, Any]:
    """
    Test Supabase connection and return status information.
    
    Returns:
        Dict containing connection status and details
    """
    # If Supabase is skipped, return a success status for local development
    if settings.skip_supabase:
        return {
            "configured": False,
            "client_available": False,
            "admin_client_available": False,
            "connection_test": False,
            "error": None,
            "skipped": True,
            "message": "Supabase skipped for local development"
        }
    
    result = {
        "configured": is_supabase_configured(),
        "client_available": False,
        "admin_client_available": False,
        "connection_test": False,
        "error": None,
        "skipped": False
    }
    
    try:
        # Test regular client
        client = get_supabase_client()
        if client:
            result["client_available"] = True
            
            # Try a simple query to test connection
            response = client.table("profiles").select("id").limit(1).execute()
            result["connection_test"] = True
            
        # Test admin client
        admin_client = get_supabase_admin_client()
        if admin_client:
            result["admin_client_available"] = True
            
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Supabase connection test failed: {e}")
    
    return result


class SupabaseService:
    """
    Service class for Supabase operations.
    
    This class provides a higher-level interface for common Supabase operations
    and handles client management and error handling.
    """
    
    def __init__(self, use_admin: bool = False):
        """
        Initialize Supabase service.
        
        Args:
            use_admin: Whether to use admin client with elevated privileges
        """
        self.use_admin = use_admin
        self._client = None
    
    @property
    def client(self):
        """Get the appropriate Supabase client."""
        if self._client is None:
            if self.use_admin:
                self._client = get_supabase_admin_client()
            else:
                self._client = get_supabase_client()
        
        if self._client is None:
            raise RuntimeError("Supabase client not available")
        
        return self._client
    
    async def execute_query(self, table: str, query_builder) -> Dict[str, Any]:
        """
        Execute a query and return results with error handling.
        
        Args:
            table: Table name
            query_builder: Supabase query builder function
            
        Returns:
            Dict containing query results or error information
        """
        try:
            response = query_builder(self.client.table(table)).execute()
            return {
                "success": True,
                "data": response.data,
                "count": getattr(response, 'count', None)
            }
        except Exception as e:
            logger.error(f"Supabase query failed for table {table}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def insert_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a record into a table.
        
        Args:
            table: Table name
            data: Record data
            
        Returns:
            Dict containing insert results
        """
        return await self.execute_query(
            table,
            lambda t: t.insert(data)
        )
    
    async def update_record(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update records in a table.
        
        Args:
            table: Table name
            data: Update data
            filters: Filter conditions
            
        Returns:
            Dict containing update results
        """
        def build_query(t):
            query = t.update(data)
            for key, value in filters.items():
                query = query.eq(key, value)
            return query
        
        return await self.execute_query(table, build_query)
    
    async def delete_record(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete records from a table.
        
        Args:
            table: Table name
            filters: Filter conditions
            
        Returns:
            Dict containing delete results
        """
        def build_query(t):
            query = t.delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            return query
        
        return await self.execute_query(table, build_query)


# Convenience functions for getting service instances
def get_supabase_service(use_admin: bool = False) -> SupabaseService:
    """Get a Supabase service instance."""
    return SupabaseService(use_admin=use_admin)


def get_supabase_admin_service() -> SupabaseService:
    """Get a Supabase service instance with admin privileges."""
    return SupabaseService(use_admin=True)