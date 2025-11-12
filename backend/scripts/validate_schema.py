#!/usr/bin/env python3
"""
Database Schema Validation Utility

This script validates the database schema against the expected structure
and checks for data integrity issues.

Usage:
    python scripts/validate_schema.py check           # Check schema integrity
    python scripts/validate_schema.py validate        # Validate data integrity
    python scripts/validate_schema.py repair          # Repair common issues
    python scripts/validate_schema.py analyze         # Analyze database statistics
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
import click
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from core.config import settings  # noqa: E402
from core.database import get_database_url  # noqa: E402


# Expected schema structure
EXPECTED_TABLES = {
    'profiles': {
        'columns': ['id', 'username', 'full_name', 'avatar_url', 'role', 'email_confirmed', 'created_at', 'updated_at'],
        'primary_key': ['id'],
        'unique_constraints': ['username'],
        'foreign_keys': []
    },
    'projects': {
        'columns': ['id', 'name', 'description', 'owner_id', 'target_domain', 'scope_rules', 'created_at', 'updated_at'],
        'primary_key': ['id'],
        'unique_constraints': [],
        'foreign_keys': [('owner_id', 'profiles', 'id')]
    },
    'scan_sessions': {
        'columns': ['id', 'project_id', 'status', 'start_time', 'end_time', 'configuration', 'stats', 'created_by'],
        'primary_key': ['id'],
        'unique_constraints': [],
        'foreign_keys': [('project_id', 'projects', 'id'), ('created_by', 'profiles', 'id')]
    },
    'discovered_urls': {
        'columns': ['id', 'session_id', 'url', 'parent_url', 'method', 'status_code', 'content_type', 'content_length', 'response_time', 'page_title', 'discovered_at'],
        'primary_key': ['id'],
        'unique_constraints': [],
        'foreign_keys': [('session_id', 'scan_sessions', 'id')]
    },
    'extracted_forms': {
        'columns': ['id', 'url_id', 'form_action', 'form_method', 'form_fields', 'csrf_tokens', 'authentication_required'],
        'primary_key': ['id'],
        'unique_constraints': [],
        'foreign_keys': [('url_id', 'discovered_urls', 'id')]
    },
    'technology_fingerprints': {
        'columns': ['id', 'url_id', 'server_software', 'programming_language', 'framework', 'cms', 'javascript_libraries', 'security_headers', 'detected_at'],
        'primary_key': ['id'],
        'unique_constraints': [],
        'foreign_keys': [('url_id', 'discovered_urls', 'id')]
    }
}


@click.group()
def cli():
    """Database schema validation commands."""


async def get_actual_schema() -> Dict[str, Any]:
    """Get the actual database schema."""
    engine = create_async_engine(get_database_url())
    
    async with engine.connect() as conn:
        # Get table information
        tables = {}
        
        # Get all table names
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'
        """))
        table_names = [row[0] for row in result.fetchall()]
        
        for table_name in table_names:
            # Get column information
            result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
            columns_info = result.fetchall()
            
            columns = []
            primary_keys = []
            
            for col_info in columns_info:
                col_name = col_info[1]
                columns.append(col_name)
                if col_info[5]:  # pk column
                    primary_keys.append(col_name)
            
            # Get foreign key information
            result = await conn.execute(text(f"PRAGMA foreign_key_list({table_name})"))
            fk_info = result.fetchall()
            
            foreign_keys = []
            for fk in fk_info:
                foreign_keys.append((fk[3], fk[2], fk[4]))  # (from_col, to_table, to_col)
            
            # Get index information for unique constraints
            result = await conn.execute(text(f"PRAGMA index_list({table_name})"))
            index_info = result.fetchall()
            
            unique_constraints = []
            for idx in index_info:
                if idx[2]:  # unique index
                    result = await conn.execute(text(f"PRAGMA index_info({idx[1]})"))
                    idx_cols = result.fetchall()
                    if len(idx_cols) == 1:  # single column unique constraint
                        unique_constraints.append(idx_cols[0][2])
            
            tables[table_name] = {
                'columns': columns,
                'primary_key': primary_keys,
                'unique_constraints': unique_constraints,
                'foreign_keys': foreign_keys
            }
    
    await engine.dispose()
    return tables


@cli.command()
def check():
    """Check database schema integrity."""
    click.echo("🔍 Checking database schema integrity...")
    
    try:
        actual_schema = asyncio.run(get_actual_schema())
        
        issues = []
        
        # Check for missing tables
        for expected_table in EXPECTED_TABLES:
            if expected_table not in actual_schema:
                issues.append(f"❌ Missing table: {expected_table}")
        
        # Check for extra tables
        for actual_table in actual_schema:
            if actual_table not in EXPECTED_TABLES:
                issues.append(f"⚠️  Extra table: {actual_table}")
        
        # Check table structure
        for table_name in EXPECTED_TABLES:
            if table_name not in actual_schema:
                continue
            
            expected = EXPECTED_TABLES[table_name]
            actual = actual_schema[table_name]
            
            # Check columns
            missing_cols = set(expected['columns']) - set(actual['columns'])
            extra_cols = set(actual['columns']) - set(expected['columns'])
            
            for col in missing_cols:
                issues.append(f"❌ Missing column in {table_name}: {col}")
            
            for col in extra_cols:
                issues.append(f"⚠️  Extra column in {table_name}: {col}")
            
            # Check primary keys
            if set(expected['primary_key']) != set(actual['primary_key']):
                issues.append(f"❌ Primary key mismatch in {table_name}: expected {expected['primary_key']}, got {actual['primary_key']}")
            
            # Check foreign keys
            expected_fks = set(expected['foreign_keys'])
            actual_fks = set(actual['foreign_keys'])
            
            missing_fks = expected_fks - actual_fks
            extra_fks = actual_fks - expected_fks
            
            for fk in missing_fks:
                issues.append(f"❌ Missing foreign key in {table_name}: {fk}")
            
            for fk in extra_fks:
                issues.append(f"⚠️  Extra foreign key in {table_name}: {fk}")
        
        # Report results
        if not issues:
            click.echo("✅ Database schema is valid!")
        else:
            click.echo(f"❌ Found {len(issues)} schema issues:")
            for issue in issues:
                click.echo(f"   {issue}")
        
        return len(issues) == 0
        
    except Exception as e:
        click.echo(f"❌ Error checking schema: {e}")
        sys.exit(1)


@cli.command()
def validate():
    """Validate data integrity."""
    click.echo("🔍 Validating data integrity...")
    
    try:
        async def check_data_integrity():
            engine = create_async_engine(get_database_url())
            issues = []
            
            async with engine.connect() as conn:
                # Check for orphaned records
                
                # 1. Projects without valid owners
                result = await conn.execute(text("""
                    SELECT p.id, p.name, p.owner_id 
                    FROM projects p 
                    LEFT JOIN profiles pr ON p.owner_id = pr.id 
                    WHERE pr.id IS NULL
                """))
                orphaned_projects = result.fetchall()
                
                for project in orphaned_projects:
                    issues.append(f"❌ Orphaned project: {project[1]} (ID: {project[0]}, owner: {project[2]})")
                
                # 2. Scan sessions without valid projects
                result = await conn.execute(text("""
                    SELECT s.id, s.project_id 
                    FROM scan_sessions s 
                    LEFT JOIN projects p ON s.project_id = p.id 
                    WHERE p.id IS NULL
                """))
                orphaned_scans = result.fetchall()
                
                for scan in orphaned_scans:
                    issues.append(f"❌ Orphaned scan session: {scan[0]} (project: {scan[1]})")
                
                # 3. URLs without valid scan sessions
                result = await conn.execute(text("""
                    SELECT u.id, u.session_id 
                    FROM discovered_urls u 
                    LEFT JOIN scan_sessions s ON u.session_id = s.id 
                    WHERE s.id IS NULL
                """))
                orphaned_urls = result.fetchall()
                
                for url in orphaned_urls:
                    issues.append(f"❌ Orphaned URL: {url[0]} (session: {url[1]})")
                
                # 4. Forms without valid URLs
                result = await conn.execute(text("""
                    SELECT f.id, f.url_id 
                    FROM extracted_forms f 
                    LEFT JOIN discovered_urls u ON f.url_id = u.id 
                    WHERE u.id IS NULL
                """))
                orphaned_forms = result.fetchall()
                
                for form in orphaned_forms:
                    issues.append(f"❌ Orphaned form: {form[0]} (URL: {form[1]})")
                
                # 5. Technology fingerprints without valid URLs
                result = await conn.execute(text("""
                    SELECT t.id, t.url_id 
                    FROM technology_fingerprints t 
                    LEFT JOIN discovered_urls u ON t.url_id = u.id 
                    WHERE u.id IS NULL
                """))
                orphaned_tech = result.fetchall()
                
                for tech in orphaned_tech:
                    issues.append(f"❌ Orphaned technology fingerprint: {tech[0]} (URL: {tech[1]})")
                
                # Check for invalid data
                
                # 6. Invalid scan statuses
                result = await conn.execute(text("""
                    SELECT id, status 
                    FROM scan_sessions 
                    WHERE status NOT IN ('pending', 'running', 'completed', 'failed', 'cancelled')
                """))
                invalid_statuses = result.fetchall()
                
                for scan in invalid_statuses:
                    issues.append(f"❌ Invalid scan status: {scan[0]} (status: {scan[1]})")
                
                # 7. Invalid user roles
                result = await conn.execute(text("""
                    SELECT id, username, role 
                    FROM profiles 
                    WHERE role NOT IN ('user', 'admin', 'moderator')
                """))
                invalid_roles = result.fetchall()
                
                for user in invalid_roles:
                    issues.append(f"❌ Invalid user role: {user[1]} (ID: {user[0]}, role: {user[2]})")
                
                # 8. Duplicate usernames
                result = await conn.execute(text("""
                    SELECT username, COUNT(*) as count 
                    FROM profiles 
                    WHERE username IS NOT NULL 
                    GROUP BY username 
                    HAVING count > 1
                """))
                duplicate_usernames = result.fetchall()
                
                for dup in duplicate_usernames:
                    issues.append(f"❌ Duplicate username: {dup[0]} ({dup[1]} occurrences)")
            
            await engine.dispose()
            return issues
        
        issues = asyncio.run(check_data_integrity())
        
        if not issues:
            click.echo("✅ Data integrity validation passed!")
        else:
            click.echo(f"❌ Found {len(issues)} data integrity issues:")
            for issue in issues:
                click.echo(f"   {issue}")
        
        return len(issues) == 0
        
    except Exception as e:
        click.echo(f"❌ Error validating data: {e}")
        sys.exit(1)


@cli.command()
def repair():
    """Repair common database issues."""
    if not settings.DEBUG:
        click.echo("❌ Database repair only allowed in development mode!")
        sys.exit(1)
    
    click.echo("🔧 Repairing database issues...")
    
    if not click.confirm("This will modify the database. Continue?"):
        click.echo("❌ Repair cancelled.")
        return
    
    try:
        async def repair_issues():
            engine = create_async_engine(get_database_url())
            repairs = []
            
            async with engine.begin() as conn:
                # 1. Remove orphaned records
                
                # Remove orphaned forms
                result = await conn.execute(text("""
                    DELETE FROM extracted_forms 
                    WHERE url_id NOT IN (SELECT id FROM discovered_urls)
                """))
                if result.rowcount > 0:
                    repairs.append(f"Removed {result.rowcount} orphaned forms")
                
                # Remove orphaned technology fingerprints
                result = await conn.execute(text("""
                    DELETE FROM technology_fingerprints 
                    WHERE url_id NOT IN (SELECT id FROM discovered_urls)
                """))
                if result.rowcount > 0:
                    repairs.append(f"Removed {result.rowcount} orphaned technology fingerprints")
                
                # Remove orphaned URLs
                result = await conn.execute(text("""
                    DELETE FROM discovered_urls 
                    WHERE session_id NOT IN (SELECT id FROM scan_sessions)
                """))
                if result.rowcount > 0:
                    repairs.append(f"Removed {result.rowcount} orphaned URLs")
                
                # Remove orphaned scan sessions
                result = await conn.execute(text("""
                    DELETE FROM scan_sessions 
                    WHERE project_id NOT IN (SELECT id FROM projects)
                """))
                if result.rowcount > 0:
                    repairs.append(f"Removed {result.rowcount} orphaned scan sessions")
                
                # Remove orphaned projects
                result = await conn.execute(text("""
                    DELETE FROM projects 
                    WHERE owner_id NOT IN (SELECT id FROM profiles)
                """))
                if result.rowcount > 0:
                    repairs.append(f"Removed {result.rowcount} orphaned projects")
                
                # 2. Fix invalid data
                
                # Fix invalid scan statuses
                result = await conn.execute(text("""
                    UPDATE scan_sessions 
                    SET status = 'failed' 
                    WHERE status NOT IN ('pending', 'running', 'completed', 'failed', 'cancelled')
                """))
                if result.rowcount > 0:
                    repairs.append(f"Fixed {result.rowcount} invalid scan statuses")
                
                # Fix invalid user roles
                result = await conn.execute(text("""
                    UPDATE profiles 
                    SET role = 'user' 
                    WHERE role NOT IN ('user', 'admin', 'moderator')
                """))
                if result.rowcount > 0:
                    repairs.append(f"Fixed {result.rowcount} invalid user roles")
            
            await engine.dispose()
            return repairs
        
        repairs = asyncio.run(repair_issues())
        
        if not repairs:
            click.echo("✅ No issues found to repair!")
        else:
            click.echo(f"✅ Completed {len(repairs)} repairs:")
            for repair in repairs:
                click.echo(f"   🔧 {repair}")
        
    except Exception as e:
        click.echo(f"❌ Error during repair: {e}")
        sys.exit(1)


@cli.command()
def analyze():
    """Analyze database statistics."""
    click.echo("📊 Analyzing database statistics...")
    
    try:
        async def get_statistics():
            engine = create_async_engine(get_database_url())
            stats = {}
            
            async with engine.connect() as conn:
                # Table row counts
                for table in EXPECTED_TABLES:
                    try:
                        result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        stats[table] = count
                    except Exception:
                        stats[table] = 0
                
                # Additional statistics
                
                # Active scans
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM scan_sessions WHERE status = 'running'
                """))
                stats['active_scans'] = result.scalar()
                
                # Completed scans
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM scan_sessions WHERE status = 'completed'
                """))
                stats['completed_scans'] = result.scalar()
                
                # Average URLs per scan
                result = await conn.execute(text("""
                    SELECT AVG(url_count) FROM (
                        SELECT COUNT(*) as url_count 
                        FROM discovered_urls 
                        GROUP BY session_id
                    )
                """))
                avg_urls = result.scalar()
                stats['avg_urls_per_scan'] = round(avg_urls or 0, 2)
                
                # Most common status codes
                result = await conn.execute(text("""
                    SELECT status_code, COUNT(*) as count 
                    FROM discovered_urls 
                    WHERE status_code IS NOT NULL 
                    GROUP BY status_code 
                    ORDER BY count DESC 
                    LIMIT 5
                """))
                stats['top_status_codes'] = result.fetchall()
                
                # Database file size
                result = await conn.execute(text("PRAGMA page_count"))
                page_count = result.scalar()
                result = await conn.execute(text("PRAGMA page_size"))
                page_size = result.scalar()
                stats['db_size_mb'] = round((page_count * page_size) / (1024 * 1024), 2)
            
            await engine.dispose()
            return stats
        
        stats = asyncio.run(get_statistics())
        
        click.echo()
        click.echo("📋 Database Statistics:")
        click.echo()
        
        # Table counts
        click.echo("📊 Table Row Counts:")
        for table, count in stats.items():
            if table in EXPECTED_TABLES:
                click.echo(f"   {table:25} {count:>8,}")
        
        click.echo()
        
        # Scan statistics
        click.echo("🔍 Scan Statistics:")
        click.echo(f"   Active scans:           {stats['active_scans']:>8,}")
        click.echo(f"   Completed scans:        {stats['completed_scans']:>8,}")
        click.echo(f"   Avg URLs per scan:      {stats['avg_urls_per_scan']:>8}")
        
        click.echo()
        
        # Status codes
        if stats['top_status_codes']:
            click.echo("🌐 Top HTTP Status Codes:")
            for status_code, count in stats['top_status_codes']:
                click.echo(f"   {status_code:3}                     {count:>8,}")
        
        click.echo()
        
        # Database size
        click.echo(f"💾 Database Size:          {stats['db_size_mb']:>8} MB")
        
    except Exception as e:
        click.echo(f"❌ Error analyzing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()