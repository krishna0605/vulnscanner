#!/usr/bin/env python3
"""
Database management CLI for VulnScanner.
Provides commands for initialization, migration, and maintenance.
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import settings
from db.init_database import init_database, reset_database
from db.versioning import get_version_manager
from migrations.migrate_to_unified_schema import run_schema_migration

console = Console()


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose: bool):
    """VulnScanner Database Management CLI"""
    setup_logging(verbose)


@cli.command()
@click.option('--force', is_flag=True, help='Force initialization even if database exists')
def init(force: bool):
    """Initialize the database with all required tables and data."""
    console.print(Panel.fit("🚀 Database Initialization", style="bold blue"))
    
    if force:
        console.print("[yellow]⚠️  Force mode enabled - existing data may be overwritten[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing database...", total=None)
        
        try:
            success = asyncio.run(init_database())
            
            if success:
                progress.update(task, description="✅ Database initialized successfully!")
                console.print("\n[green]✅ Database initialization completed![/green]")
                
                # Show database info
                show_database_info()
            else:
                progress.update(task, description="❌ Database initialization failed!")
                console.print("\n[red]❌ Database initialization failed![/red]")
                sys.exit(1)
                
        except Exception as e:
            progress.update(task, description="❌ Database initialization failed!")
            console.print(f"\n[red]❌ Error: {e}[/red]")
            sys.exit(1)


@cli.command()
@click.option('--backup/--no-backup', default=True, help='Backup old tables before migration')
@click.confirmation_option(prompt='Are you sure you want to run the migration?')
def migrate(backup: bool):
    """Migrate from old schema to unified schema."""
    console.print(Panel.fit("🔄 Schema Migration", style="bold yellow"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running schema migration...", total=None)
        
        try:
            success = asyncio.run(run_schema_migration(backup_old_tables=backup))
            
            if success:
                progress.update(task, description="✅ Migration completed successfully!")
                console.print("\n[green]✅ Schema migration completed![/green]")
            else:
                progress.update(task, description="❌ Migration failed!")
                console.print("\n[red]❌ Schema migration failed![/red]")
                sys.exit(1)
                
        except Exception as e:
            progress.update(task, description="❌ Migration failed!")
            console.print(f"\n[red]❌ Error: {e}[/red]")
            sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to reset the database? This will delete ALL data!')
def reset(force: bool = False):
    """Reset the database by dropping and recreating all tables."""
    console.print(Panel.fit("⚠️  Database Reset", style="bold red"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Resetting database...", total=None)
        
        try:
            success = asyncio.run(reset_database())
            
            if success:
                progress.update(task, description="✅ Database reset completed!")
                console.print("\n[green]✅ Database reset and reinitialized![/green]")
            else:
                progress.update(task, description="❌ Database reset failed!")
                console.print("\n[red]❌ Database reset failed![/red]")
                sys.exit(1)
                
        except Exception as e:
            progress.update(task, description="❌ Database reset failed!")
            console.print(f"\n[red]❌ Error: {e}[/red]")
            sys.exit(1)


@cli.command()
def status():
    """Show database status and information."""
    console.print(Panel.fit("📊 Database Status", style="bold green"))
    show_database_info()


@cli.command()
def version():
    """Show database schema version information."""
    console.print(Panel.fit("📋 Schema Version", style="bold cyan"))
    
    async def get_version_info():
        try:
            version_manager = await get_version_manager()
            current_version = await version_manager.get_current_version()
            
            table = Table(title="Schema Version Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Current Version", str(current_version.version))
            table.add_row("Applied At", current_version.applied_at.strftime("%Y-%m-%d %H:%M:%S"))
            table.add_row("Description", current_version.description or "N/A")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]❌ Error getting version info: {e}[/red]")
    
    asyncio.run(get_version_info())


def show_database_info():
    """Display database configuration information."""
    table = Table(title="Database Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # Database URLs
    if settings.database_url:
        db_type = "SQLite" if "sqlite" in settings.database_url else "PostgreSQL"
        table.add_row("Database Type", db_type)
        
        if "sqlite" in settings.database_url:
            table.add_row("Database File", settings.database_url.split("///")[-1])
        else:
            table.add_row("Database URL", settings.database_url[:50] + "..." if len(settings.database_url) > 50 else settings.database_url)
    
    if settings.supabase_db_url:
        table.add_row("Supabase URL", "Configured ✅")
    
    # Environment
    table.add_row("Environment", settings.app_env)
    table.add_row("Debug Mode", "Enabled" if settings.debug else "Disabled")
    table.add_row("Database Echo", "Enabled" if settings.db_echo else "Disabled")
    
    console.print(table)


@cli.command()
@click.argument('sql_file', type=click.Path(exists=True))
def execute_sql(sql_file: str):
    """Execute SQL commands from a file."""
    console.print(Panel.fit(f"📝 Executing SQL: {sql_file}", style="bold magenta"))
    
    async def run_sql():
        try:
            from db.session import async_session
            from sqlalchemy import text
            
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            async with async_session() as session:
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for i, statement in enumerate(statements, 1):
                    console.print(f"Executing statement {i}/{len(statements)}...")
                    await session.execute(text(statement))
                
                await session.commit()
                console.print(f"[green]✅ Executed {len(statements)} SQL statements successfully![/green]")
                
        except Exception as e:
            console.print(f"[red]❌ Error executing SQL: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(run_sql())


@cli.command()
@click.option('--table', help='Specific table to check')
def check_tables(table: Optional[str]):
    """Check database tables and their row counts."""
    console.print(Panel.fit("🔍 Table Information", style="bold blue"))
    
    async def check_db_tables():
        try:
            from db.session import async_session
            from sqlalchemy import text
            
            async with async_session() as session:
                # Get all table names
                if "sqlite" in (settings.database_url or ""):
                    result = await session.execute(
                        text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    )
                else:
                    result = await session.execute(
                        text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                    )
                
                tables = [row[0] for row in result.fetchall()]
                
                if table:
                    tables = [t for t in tables if table.lower() in t.lower()]
                
                if not tables:
                    console.print("[yellow]No tables found[/yellow]")
                    return
                
                # Create table with counts
                info_table = Table(title="Database Tables")
                info_table.add_column("Table Name", style="cyan")
                info_table.add_column("Row Count", style="green")
                info_table.add_column("Status", style="yellow")
                
                for table_name in sorted(tables):
                    try:
                        count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = count_result.scalar()
                        status = "✅ OK"
                    except Exception as e:
                        count = "Error"
                        status = f"❌ {str(e)[:30]}..."
                    
                    info_table.add_row(table_name, str(count), status)
                
                console.print(info_table)
                
        except Exception as e:
            console.print(f"[red]❌ Error checking tables: {e}[/red]")
    
    asyncio.run(check_db_tables())


if __name__ == '__main__':
    cli()