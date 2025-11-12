#!/usr/bin/env python3
"""
Initialize SQLite database with required tables.
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from db.session import init_db, engine  # noqa: E402
# Import models using conditional imports to avoid conflicts

async def main():
    """Initialize the SQLite database."""
    print("🚀 Initializing SQLite database...")
    
    try:
        # Create all tables
        await init_db()
        print("✅ Database tables created successfully!")
        
        # Close engine
        await engine.dispose()
        
        print("🎉 Database initialization completed!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())