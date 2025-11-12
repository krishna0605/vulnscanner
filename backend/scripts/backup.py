#!/usr/bin/env python3
"""
Database Backup and Restore Utility

This script provides utilities for backing up and restoring the SQLite database
for the Enhanced Vulnerability Scanner.

Usage:
    python scripts/backup.py create [--name backup_name]    # Create backup
    python scripts/backup.py list                           # List backups
    python scripts/backup.py restore <backup_name>          # Restore backup
    python scripts/backup.py cleanup [--keep 5]             # Cleanup old backups
    python scripts/backup.py export <format>                # Export data (json/csv)
"""

import asyncio
import sys
import shutil
import json
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import click
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from core.config import settings  # noqa: E402
from core.database import get_database_url  # noqa: E402


def get_backup_dir() -> Path:
    """Get backup directory path."""
    backup_dir = backend_path / "backups"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def get_database_path() -> Path:
    """Get current database file path."""
    db_url = get_database_url()
    if db_url.startswith("sqlite+aiosqlite:///"):
        db_path = db_url.replace("sqlite+aiosqlite:///", "")
        return Path(db_path)
    else:
        raise ValueError("Backup only supported for SQLite databases")


@click.group()
def cli():
    """Database backup and restore commands."""


@cli.command()
@click.option('--name', '-n', help='Backup name (default: timestamp)')
def create(name: Optional[str]):
    """Create a database backup."""
    try:
        db_path = get_database_path()
        backup_dir = get_backup_dir()
        
        if not db_path.exists():
            click.echo(f"❌ Database file not found: {db_path}")
            sys.exit(1)
        
        # Generate backup name
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"backup_{timestamp}"
        
        backup_path = backup_dir / f"{name}.db"
        
        # Create backup
        click.echo(f"📦 Creating backup: {name}")
        shutil.copy2(db_path, backup_path)
        
        # Create metadata file
        metadata = {
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "original_path": str(db_path),
            "backup_path": str(backup_path),
            "file_size": backup_path.stat().st_size,
            "version": "1.0"
        }
        
        metadata_path = backup_dir / f"{name}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        click.echo("✅ Backup created successfully!")
        click.echo(f"   File: {backup_path}")
        click.echo(f"   Size: {metadata['file_size']:,} bytes")
        
    except Exception as e:
        click.echo(f"❌ Error creating backup: {e}")
        sys.exit(1)


@cli.command()
def list():
    """List all available backups."""
    try:
        backup_dir = get_backup_dir()
        
        # Find all backup files
        backups = []
        for db_file in backup_dir.glob("*.db"):
            metadata_file = backup_dir / f"{db_file.stem}.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            else:
                # Create basic metadata for files without it
                stat = db_file.stat()
                backups.append({
                    "name": db_file.stem,
                    "created_at": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
                    "file_size": stat.st_size,
                    "backup_path": str(db_file)
                })
        
        if not backups:
            click.echo("📭 No backups found.")
            return
        
        # Sort by creation date
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        click.echo("📋 Available backups:")
        click.echo()
        
        for backup in backups:
            created_at = datetime.fromisoformat(backup["created_at"].replace('Z', '+00:00'))
            size_mb = backup["file_size"] / (1024 * 1024)
            
            click.echo(f"  🗃️  {backup['name']}")
            click.echo(f"      Created: {created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            click.echo(f"      Size: {size_mb:.2f} MB")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error listing backups: {e}")
        sys.exit(1)


@cli.command()
@click.argument('backup_name')
@click.option('--force', '-f', is_flag=True, help='Force restore without confirmation')
def restore(backup_name: str, force: bool):
    """Restore database from backup."""
    if not settings.DEBUG and not force:
        click.echo("❌ Database restore only allowed in development mode or with --force!")
        sys.exit(1)
    
    try:
        backup_dir = get_backup_dir()
        backup_path = backup_dir / f"{backup_name}.db"
        
        if not backup_path.exists():
            click.echo(f"❌ Backup not found: {backup_name}")
            click.echo("Use 'list' command to see available backups.")
            sys.exit(1)
        
        db_path = get_database_path()
        
        click.echo(f"🔄 Restoring backup: {backup_name}")
        click.echo(f"   From: {backup_path}")
        click.echo(f"   To: {db_path}")
        
        if not force and not click.confirm("This will overwrite the current database. Continue?"):
            click.echo("❌ Restore cancelled.")
            return
        
        # Create backup of current database
        if db_path.exists():
            current_backup = backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db_path, current_backup)
            click.echo(f"📦 Current database backed up to: {current_backup.name}")
        
        # Restore backup
        shutil.copy2(backup_path, db_path)
        
        click.echo("✅ Database restored successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error restoring backup: {e}")
        sys.exit(1)


@cli.command()
@click.option('--keep', '-k', default=5, help='Number of backups to keep (default: 5)')
def cleanup(keep: int):
    """Cleanup old backups, keeping the most recent ones."""
    try:
        backup_dir = get_backup_dir()
        
        # Find all backup files with metadata
        backups = []
        for db_file in backup_dir.glob("*.db"):
            metadata_file = backup_dir / f"{db_file.stem}.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                backups.append((db_file, metadata_file, metadata))
            else:
                # Files without metadata
                stat = db_file.stat()
                metadata = {
                    "name": db_file.stem,
                    "created_at": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat()
                }
                backups.append((db_file, None, metadata))
        
        if len(backups) <= keep:
            click.echo(f"📭 Only {len(backups)} backups found, nothing to cleanup.")
            return
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x[2]["created_at"], reverse=True)
        
        # Keep the most recent ones, delete the rest
        to_delete = backups[keep:]
        
        click.echo(f"🧹 Cleaning up {len(to_delete)} old backups (keeping {keep} most recent):")
        
        for db_file, metadata_file, metadata in to_delete:
            click.echo(f"   Deleting: {metadata['name']}")
            db_file.unlink()
            if metadata_file:
                metadata_file.unlink()
        
        click.echo("✅ Cleanup completed!")
        
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}")
        sys.exit(1)


@cli.command()
@click.argument('format', type=click.Choice(['json', 'csv']))
@click.option('--output', '-o', help='Output file path')
@click.option('--table', '-t', help='Specific table to export (default: all)')
def export(format: str, output: Optional[str], table: Optional[str]):
    """Export database data to JSON or CSV format."""
    try:
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"export_{timestamp}.{format}"
        
        click.echo(f"📤 Exporting database to {format.upper()} format...")
        
        async def export_data():
            engine = create_async_engine(get_database_url())
            
            async with engine.connect() as conn:
                # Get all table names
                if table:
                    tables = [table]
                else:
                    result = await conn.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'
                    """))
                    tables = [row[0] for row in result.fetchall()]
                
                export_data = {}
                
                for table_name in tables:
                    click.echo(f"   Exporting table: {table_name}")
                    result = await conn.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    export_data[table_name] = [
                        dict(zip(columns, row)) for row in rows
                    ]
            
            await engine.dispose()
            return export_data
        
        data = asyncio.run(export_data())
        
        # Write to file
        if format == 'json':
            with open(output, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        elif format == 'csv':
            # For CSV, create separate files for each table
            output_dir = Path(output).stem
            Path(output_dir).mkdir(exist_ok=True)
            
            for table_name, rows in data.items():
                if rows:
                    csv_file = Path(output_dir) / f"{table_name}.csv"
                    with open(csv_file, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                        writer.writeheader()
                        writer.writerows(rows)
                    click.echo(f"   Created: {csv_file}")
        
        click.echo(f"✅ Export completed: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error during export: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()