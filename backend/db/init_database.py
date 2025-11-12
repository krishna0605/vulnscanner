"""
Unified database initialization for VulnScanner.
Works with both SQLite (development) and PostgreSQL (production/Supabase).
"""
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.config import settings
from db.session import Base, async_session
from db.versioning import ensure_schema_compatibility
from models.unified_models import (
    VulnerabilityType
)

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """
    Handles database initialization for both SQLite and PostgreSQL.
    """
    
    def __init__(self):
        self.is_sqlite = "sqlite" in (settings.database_url or "")
        self.is_postgresql = "postgresql" in (settings.supabase_db_url or "")
    
    async def create_tables(self, session: AsyncSession) -> bool:
        """Create all database tables."""
        try:
            logger.info("Creating database tables...")
            
            # Get the engine from the session
            engine = session.bind
            
            # Create all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✅ Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            return False
    
    async def seed_vulnerability_types(self, session: AsyncSession) -> bool:
        """Seed the database with default vulnerability types."""
        try:
            logger.info("Seeding vulnerability types...")
            
            # Check if vulnerability types already exist
            result = await session.execute(
                text("SELECT COUNT(*) FROM vulnerability_types")
            )
            count = result.scalar()
            
            if count > 0:
                logger.info(f"Vulnerability types already seeded ({count} types found)")
                return True
            
            # Default OWASP Top 10 vulnerability types
            default_vuln_types = [
                {
                    "name": "SQL Injection",
                    "category": "injection",
                    "severity": "high",
                    "description": "SQL injection vulnerabilities allow attackers to interfere with database queries",
                    "cwe_id": "CWE-89",
                    "owasp_category": "A03:2021"
                },
                {
                    "name": "Cross-Site Scripting (XSS)",
                    "category": "injection",
                    "severity": "medium",
                    "description": "XSS vulnerabilities allow attackers to inject malicious scripts into web pages",
                    "cwe_id": "CWE-79",
                    "owasp_category": "A03:2021"
                },
                {
                    "name": "Broken Authentication",
                    "category": "authentication",
                    "severity": "high",
                    "description": "Authentication mechanisms are implemented incorrectly",
                    "cwe_id": "CWE-287",
                    "owasp_category": "A07:2021"
                },
                {
                    "name": "Sensitive Data Exposure",
                    "category": "exposure",
                    "severity": "high",
                    "description": "Sensitive data is not properly protected",
                    "cwe_id": "CWE-200",
                    "owasp_category": "A02:2021"
                },
                {
                    "name": "Security Misconfiguration",
                    "category": "configuration",
                    "severity": "medium",
                    "description": "Security settings are not properly configured",
                    "cwe_id": "CWE-16",
                    "owasp_category": "A05:2021"
                },
                {
                    "name": "Broken Access Control",
                    "category": "authorization",
                    "severity": "high",
                    "description": "Access control restrictions are not properly enforced",
                    "cwe_id": "CWE-284",
                    "owasp_category": "A01:2021"
                },
                {
                    "name": "Cryptographic Failures",
                    "category": "cryptography",
                    "severity": "high",
                    "description": "Cryptographic functions are not properly implemented",
                    "cwe_id": "CWE-327",
                    "owasp_category": "A02:2021"
                },
                {
                    "name": "Insecure Design",
                    "category": "business_logic",
                    "severity": "medium",
                    "description": "Design flaws that lead to security vulnerabilities",
                    "cwe_id": "CWE-1021",
                    "owasp_category": "A04:2021"
                }
            ]
            
            # Insert vulnerability types
            for vuln_data in default_vuln_types:
                vuln_type = VulnerabilityType(**vuln_data)
                session.add(vuln_type)
            
            await session.commit()
            logger.info(f"✅ Seeded {len(default_vuln_types)} vulnerability types")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to seed vulnerability types: {e}")
            await session.rollback()
            return False
    
    async def create_indexes(self, session: AsyncSession) -> bool:
        """Create database indexes for performance."""
        try:
            logger.info("Creating database indexes...")
            
            # Define indexes for better performance
            indexes = [
                # Profile indexes
                "CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email)",
                "CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username)",
                "CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role)",
                
                # Project indexes
                "CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id)",
                "CREATE INDEX IF NOT EXISTS idx_projects_domain ON projects(target_domain)",
                "CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at)",
                
                # Scan session indexes
                "CREATE INDEX IF NOT EXISTS idx_scan_sessions_project ON scan_sessions(project_id)",
                "CREATE INDEX IF NOT EXISTS idx_scan_sessions_status ON scan_sessions(status)",
                "CREATE INDEX IF NOT EXISTS idx_scan_sessions_start_time ON scan_sessions(start_time)",
                
                # Discovered URL indexes
                "CREATE INDEX IF NOT EXISTS idx_discovered_urls_session ON discovered_urls(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_discovered_urls_status ON discovered_urls(status_code)",
                "CREATE INDEX IF NOT EXISTS idx_discovered_urls_discovered ON discovered_urls(discovered_at)",
                
                # Vulnerability indexes
                "CREATE INDEX IF NOT EXISTS idx_vulnerabilities_session ON vulnerabilities(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity)",
                "CREATE INDEX IF NOT EXISTS idx_vulnerabilities_status ON vulnerabilities(status)",
                "CREATE INDEX IF NOT EXISTS idx_vulnerabilities_type ON vulnerabilities(vulnerability_type_id)",
                
                # Dashboard metrics indexes
                "CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_user ON dashboard_metrics(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_type ON dashboard_metrics(metric_type)",
                "CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_recorded ON dashboard_metrics(recorded_at)",
                
                # Realtime updates indexes
                "CREATE INDEX IF NOT EXISTS idx_realtime_updates_user ON realtime_updates(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_realtime_updates_processed ON realtime_updates(processed)",
                "CREATE INDEX IF NOT EXISTS idx_realtime_updates_created ON realtime_updates(created_at)"
            ]
            
            # Execute index creation
            for index_sql in indexes:
                try:
                    await session.execute(text(index_sql))
                except Exception as e:
                    # Some indexes might already exist, that's okay
                    logger.debug(f"Index creation note: {e}")
            
            await session.commit()
            logger.info("✅ Database indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create database indexes: {e}")
            await session.rollback()
            return False
    
    async def verify_database(self, session: AsyncSession) -> bool:
        """Verify database integrity and functionality."""
        try:
            logger.info("Verifying database integrity...")
            
            # Test basic table access
            tables_to_test = [
                ("profiles", "SELECT COUNT(*) FROM profiles"),
                ("projects", "SELECT COUNT(*) FROM projects"),
                ("scan_sessions", "SELECT COUNT(*) FROM scan_sessions"),
                ("vulnerability_types", "SELECT COUNT(*) FROM vulnerability_types"),
                ("vulnerabilities", "SELECT COUNT(*) FROM vulnerabilities")
            ]
            
            for table_name, query in tables_to_test:
                try:
                    result = await session.execute(text(query))
                    count = result.scalar()
                    logger.debug(f"Table {table_name}: {count} records")
                except Exception as e:
                    logger.error(f"Failed to query table {table_name}: {e}")
                    return False
            
            logger.info("✅ Database verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database verification failed: {e}")
            return False
    
    async def initialize_database(self) -> bool:
        """Initialize the complete database."""
        try:
            logger.info("Starting database initialization...")
            
            async with async_session() as session:
                # Step 1: Create tables
                if not await self.create_tables(session):
                    return False
                
                # Step 2: Initialize versioning
                if not await ensure_schema_compatibility(session):
                    return False
                
                # Step 3: Create indexes
                if not await self.create_indexes(session):
                    return False
                
                # Step 4: Seed data
                if not await self.seed_vulnerability_types(session):
                    return False
                
                # Step 5: Verify database
                if not await self.verify_database(session):
                    return False
                
                logger.info("🎉 Database initialization completed successfully!")
                return True
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False


async def init_database() -> bool:
    """Initialize the database with all required tables and data."""
    initializer = DatabaseInitializer()
    return await initializer.initialize_database()


async def reset_database() -> bool:
    """Reset the database by dropping and recreating all tables."""
    try:
        logger.warning("Resetting database - all data will be lost!")
        
        async with async_session() as session:
            engine = session.bind
            
            # Drop all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("Dropped all tables")
            
            # Recreate database
            initializer = DatabaseInitializer()
            return await initializer.initialize_database()
            
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run database initialization
    asyncio.run(init_database())