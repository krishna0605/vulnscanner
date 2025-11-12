"""
Migration script to transition from old database schema to unified schema.
Handles data migration from existing SQLite models to unified models.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.config import settings
from db.session import async_session
from db.init_database import DatabaseInitializer
from models.unified_models import Profile, Project

logger = logging.getLogger(__name__)


class SchemaMigrator:
    """
    Handles migration from old schema to unified schema.
    """
    
    def __init__(self):
        self.is_sqlite = "sqlite" in (settings.database_url or "")
        self.migration_log: List[str] = []
    
    def log_migration(self, message: str):
        """Log migration step."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.migration_log.append(log_entry)
        logger.info(message)
    
    async def check_old_tables_exist(self, session: AsyncSession) -> Dict[str, bool]:
        """Check which old tables exist in the database."""
        tables_to_check = ["users", "projects", "scan_sessions"]
        existing_tables = {}
        
        for table in tables_to_check:
            try:
                # Try to query the table
                await session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                existing_tables[table] = True
                self.log_migration(f"Found existing table: {table}")
            except Exception:
                existing_tables[table] = False
                self.log_migration(f"Table not found: {table}")
        
        return existing_tables
    
    async def migrate_users_to_profiles(self, session: AsyncSession) -> bool:
        """Migrate users table to profiles table."""
        try:
            self.log_migration("Starting users -> profiles migration...")
            
            # Check if old users table exists
            try:
                result = await session.execute(text("SELECT * FROM users"))
                users = result.fetchall()
            except Exception:
                self.log_migration("No users table found, skipping user migration")
                return True
            
            if not users:
                self.log_migration("No users to migrate")
                return True
            
            # Check if profiles table already has data
            result = await session.execute(text("SELECT COUNT(*) FROM profiles"))
            profile_count = result.scalar()
            
            if profile_count > 0:
                self.log_migration(f"Profiles table already has {profile_count} records, skipping migration")
                return True
            
            # Migrate each user to profile
            migrated_count = 0
            for user in users:
                try:
                    # Create profile from user data
                    profile_data = {
                        "id": str(uuid4()),  # Generate new UUID
                        "email": user.email if hasattr(user, 'email') else f"user_{user.id}@example.com",
                        "username": user.email.split('@')[0] if hasattr(user, 'email') else f"user_{user.id}",
                        "full_name": user.full_name if hasattr(user, 'full_name') else f"User {user.id}",
                        "role": "user",  # Default role
                        "is_active": True,
                        "created_at": user.created_at if hasattr(user, 'created_at') else datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                    
                    # Insert profile
                    profile = Profile(**profile_data)
                    session.add(profile)
                    migrated_count += 1
                    
                    # Store mapping for project migration
                    await session.execute(
                        text("INSERT OR IGNORE INTO user_id_mapping (old_id, new_id) VALUES (:old_id, :new_id)"),
                        {"old_id": user.id, "new_id": profile_data["id"]}
                    )
                    
                except Exception as e:
                    self.log_migration(f"Failed to migrate user {user.id}: {e}")
                    continue
            
            await session.commit()
            self.log_migration(f"✅ Migrated {migrated_count} users to profiles")
            return True
            
        except Exception as e:
            self.log_migration(f"❌ User migration failed: {e}")
            await session.rollback()
            return False
    
    async def migrate_projects(self, session: AsyncSession) -> bool:
        """Migrate projects table with updated schema."""
        try:
            self.log_migration("Starting projects migration...")
            
            # Check if old projects table exists
            try:
                result = await session.execute(text("SELECT * FROM projects"))
                projects = result.fetchall()
            except Exception:
                self.log_migration("No projects table found, skipping project migration")
                return True
            
            if not projects:
                self.log_migration("No projects to migrate")
                return True
            
            # Migrate each project
            migrated_count = 0
            for project in projects:
                try:
                    # Get new owner ID from mapping
                    owner_result = await session.execute(
                        text("SELECT new_id FROM user_id_mapping WHERE old_id = :old_id"),
                        {"old_id": project.owner_id}
                    )
                    owner_mapping = owner_result.fetchone()
                    
                    if not owner_mapping:
                        # Create a default profile for orphaned projects
                        default_profile_id = str(uuid4())
                        default_profile = Profile(
                            id=default_profile_id,
                            email="admin@vulnscanner.local",
                            username="admin",
                            full_name="System Administrator",
                            role="admin",
                            is_active=True
                        )
                        session.add(default_profile)
                        owner_id = default_profile_id
                    else:
                        owner_id = owner_mapping.new_id
                    
                    # Create updated project
                    project_data = {
                        "id": str(uuid4()),
                        "name": project.name,
                        "description": project.description if hasattr(project, 'description') else "",
                        "owner_id": owner_id,
                        "target_domain": project.target_domain,
                        "scope_rules": [],  # Default empty scope rules
                        "created_at": project.created_at if hasattr(project, 'created_at') else datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                    
                    new_project = Project(**project_data)
                    session.add(new_project)
                    migrated_count += 1
                    
                except Exception as e:
                    self.log_migration(f"Failed to migrate project {project.id}: {e}")
                    continue
            
            await session.commit()
            self.log_migration(f"✅ Migrated {migrated_count} projects")
            return True
            
        except Exception as e:
            self.log_migration(f"❌ Project migration failed: {e}")
            await session.rollback()
            return False
    
    async def create_migration_tables(self, session: AsyncSession) -> bool:
        """Create temporary tables for migration tracking."""
        try:
            # Create user ID mapping table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS user_id_mapping (
                    old_id INTEGER PRIMARY KEY,
                    new_id TEXT NOT NULL
                )
            """))
            
            # Create migration log table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS migration_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            await session.commit()
            return True
            
        except Exception as e:
            self.log_migration(f"Failed to create migration tables: {e}")
            return False
    
    async def cleanup_old_tables(self, session: AsyncSession, backup: bool = True) -> bool:
        """Clean up old tables after successful migration."""
        try:
            if backup:
                self.log_migration("Creating backup of old tables...")
                
                # Rename old tables to backup names
                old_tables = ["users", "projects", "scan_sessions"]
                for table in old_tables:
                    try:
                        await session.execute(
                            text(f"ALTER TABLE {table} RENAME TO {table}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                        )
                        self.log_migration(f"Backed up table: {table}")
                    except Exception as e:
                        self.log_migration(f"Could not backup table {table}: {e}")
            
            await session.commit()
            self.log_migration("✅ Old tables backed up successfully")
            return True
            
        except Exception as e:
            self.log_migration(f"❌ Cleanup failed: {e}")
            return False
    
    async def save_migration_log(self, session: AsyncSession) -> bool:
        """Save migration log to database."""
        try:
            for log_entry in self.migration_log:
                await session.execute(
                    text("INSERT INTO migration_log (timestamp, message) VALUES (:timestamp, :message)"),
                    {
                        "timestamp": datetime.now().isoformat(),
                        "message": log_entry
                    }
                )
            
            await session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save migration log: {e}")
            return False
    
    async def run_migration(self, backup_old_tables: bool = True) -> bool:
        """Run the complete migration process."""
        try:
            self.log_migration("🚀 Starting schema migration to unified models...")
            
            async with async_session() as session:
                # Step 1: Create migration tracking tables
                if not await self.create_migration_tables(session):
                    return False
                
                # Step 2: Check existing tables
                existing_tables = await self.check_old_tables_exist(session)
                
                # Step 3: Initialize new unified schema
                initializer = DatabaseInitializer()
                if not await initializer.create_tables(session):
                    self.log_migration("❌ Failed to create unified schema tables")
                    return False
                
                # Step 4: Migrate data if old tables exist
                if existing_tables.get("users", False):
                    if not await self.migrate_users_to_profiles(session):
                        return False
                
                if existing_tables.get("projects", False):
                    if not await self.migrate_projects(session):
                        return False
                
                # Step 5: Initialize vulnerability types and indexes
                if not await initializer.seed_vulnerability_types(session):
                    return False
                
                if not await initializer.create_indexes(session):
                    return False
                
                # Step 6: Cleanup old tables
                if backup_old_tables and any(existing_tables.values()):
                    if not await self.cleanup_old_tables(session, backup=True):
                        return False
                
                # Step 7: Save migration log
                await self.save_migration_log(session)
                
                self.log_migration("🎉 Schema migration completed successfully!")
                return True
                
        except Exception as e:
            self.log_migration(f"❌ Migration failed: {e}")
            return False


async def run_schema_migration(backup_old_tables: bool = True) -> bool:
    """Run the schema migration."""
    migrator = SchemaMigrator()
    return await migrator.run_migration(backup_old_tables)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migration
    asyncio.run(run_schema_migration())