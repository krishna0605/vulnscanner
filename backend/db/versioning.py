"""
Database versioning and schema management for VulnScanner.
Tracks schema versions and provides migration utilities.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import Base

logger = logging.getLogger(__name__)


class SchemaVersion(Base):
    """
    Schema version tracking table.
    """
    __tablename__ = "schema_versions"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    applied_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    
    # JSON field for migration metadata
    _metadata: Mapped[str] = mapped_column("migration_metadata", sa.Text, default="{}")
    
    @property
    def migration_metadata(self) -> Dict[str, Any]:
        """Get migration metadata as a Python dict"""
        try:
            return json.loads(self._metadata) if self._metadata else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @migration_metadata.setter
    def migration_metadata(self, value: Dict[str, Any]):
        """Set migration metadata from a Python dict"""
        self._metadata = json.dumps(value) if value is not None else "{}"


class DatabaseVersionManager:
    """
    Manages database schema versions and migrations.
    """
    
    # Current schema version
    CURRENT_VERSION = "1.0.0"
    
    # Version history with descriptions
    VERSION_HISTORY = [
        {
            "version": "1.0.0",
            "description": "Initial unified schema with SQLite/PostgreSQL compatibility",
            "changes": [
                "Created unified models for cross-database compatibility",
                "Added Profile model extending Supabase auth.users",
                "Added Project model with JSON scope rules",
                "Added ScanSession model with configuration and stats",
                "Added DiscoveredUrl model for crawl results",
                "Added ExtractedForm model for form analysis",
                "Added TechnologyFingerprint model for tech detection",
                "Added VulnerabilityType and Vulnerability models",
                "Added DashboardMetric and RealtimeUpdate models",
                "Added schema versioning system"
            ]
        }
    ]
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_current_version(self) -> Optional[str]:
        """Get the current database schema version."""
        try:
            result = await self.session.execute(
                sa.select(SchemaVersion.version)
                .order_by(SchemaVersion.applied_at.desc())
                .limit(1)
            )
            version = result.scalar_one_or_none()
            return version
        except Exception as e:
            logger.warning(f"Could not get current version: {e}")
            return None
    
    async def is_version_applied(self, version: str) -> bool:
        """Check if a specific version has been applied."""
        try:
            result = await self.session.execute(
                sa.select(SchemaVersion.id)
                .where(SchemaVersion.version == version)
            )
            return result.scalar_one_or_none() is not None
        except Exception:
            return False
    
    async def apply_version(self, version: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Apply a new schema version."""
        try:
            # Check if version already exists
            if await self.is_version_applied(version):
                logger.info(f"Version {version} already applied")
                return True
            
            # Create new version record
            schema_version = SchemaVersion(
                version=version,
                description=description
            )
            schema_version.migration_metadata = metadata or {}
            
            self.session.add(schema_version)
            await self.session.commit()
            
            logger.info(f"Applied schema version {version}: {description}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply version {version}: {e}")
            await self.session.rollback()
            return False
    
    async def get_version_history(self) -> List[Dict[str, Any]]:
        """Get the complete version history."""
        try:
            result = await self.session.execute(
                sa.select(SchemaVersion)
                .order_by(SchemaVersion.applied_at.asc())
            )
            versions = result.scalars().all()
            
            return [
                {
                    "version": v.version,
                    "description": v.description,
                    "applied_at": v.applied_at,
                    "metadata": v.migration_metadata
                }
                for v in versions
            ]
        except Exception as e:
            logger.error(f"Failed to get version history: {e}")
            return []
    
    async def initialize_versioning(self) -> bool:
        """Initialize the versioning system with the current schema."""
        try:
            # Check if versioning table exists
            current_version = await self.get_current_version()
            
            if current_version is None:
                # Apply the current version
                version_info = self.VERSION_HISTORY[0]  # Latest version
                await self.apply_version(
                    version_info["version"],
                    version_info["description"],
                    {"changes": version_info["changes"]}
                )
                logger.info("Initialized database versioning system")
                return True
            else:
                logger.info(f"Versioning system already initialized at version {current_version}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize versioning: {e}")
            return False
    
    async def check_schema_compatibility(self) -> Dict[str, Any]:
        """Check if the current database schema is compatible."""
        try:
            current_version = await self.get_current_version()
            
            if current_version is None:
                return {
                    "compatible": False,
                    "current_version": None,
                    "expected_version": self.CURRENT_VERSION,
                    "message": "Database versioning not initialized"
                }
            
            if current_version == self.CURRENT_VERSION:
                return {
                    "compatible": True,
                    "current_version": current_version,
                    "expected_version": self.CURRENT_VERSION,
                    "message": "Schema is up to date"
                }
            else:
                return {
                    "compatible": False,
                    "current_version": current_version,
                    "expected_version": self.CURRENT_VERSION,
                    "message": f"Schema version mismatch. Current: {current_version}, Expected: {self.CURRENT_VERSION}"
                }
                
        except Exception as e:
            logger.error(f"Failed to check schema compatibility: {e}")
            return {
                "compatible": False,
                "current_version": None,
                "expected_version": self.CURRENT_VERSION,
                "message": f"Error checking compatibility: {e}"
            }


async def get_version_manager(session: AsyncSession) -> DatabaseVersionManager:
    """Get a database version manager instance."""
    return DatabaseVersionManager(session)


async def ensure_schema_compatibility(session: AsyncSession) -> bool:
    """Ensure the database schema is compatible with the current version."""
    try:
        version_manager = await get_version_manager(session)
        compatibility = await version_manager.check_schema_compatibility()
        
        if not compatibility["compatible"]:
            logger.warning(f"Schema compatibility issue: {compatibility['message']}")
            
            # Try to initialize versioning if not present
            if compatibility["current_version"] is None:
                logger.info("Attempting to initialize database versioning...")
                success = await version_manager.initialize_versioning()
                if success:
                    logger.info("Database versioning initialized successfully")
                    return True
                else:
                    logger.error("Failed to initialize database versioning")
                    return False
            else:
                logger.error("Schema version mismatch requires manual migration")
                return False
        else:
            logger.info(f"Schema compatibility check passed: {compatibility['message']}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to ensure schema compatibility: {e}")
        return False