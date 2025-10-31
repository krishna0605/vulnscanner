#!/usr/bin/env python3
"""
Test script to check database schema and content for scan functionality.
"""
import sqlite3
import json
from datetime import datetime, timezone
import uuid

def check_database_schema():
    """Check database schema and content."""
    db_path = 'dev.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Database Schema Check ===")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables found: {[table[0] for table in tables]}")
        
        # Check each table schema
        for table in tables:
            table_name = table[0]
            print(f"\n--- {table_name} table ---")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Row count: {count}")
            
            # Show sample data if exists
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print("Sample data:")
                for row in rows:
                    print(f"  {row}")
        
        print("\n=== Creating test data if needed ===")
        
        # Check if we have users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("Creating test user...")
            cursor.execute("""
                INSERT INTO users (email, password_hash, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                'test@example.com',
                'hashed_password_placeholder',
                True,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat()
            ))
            print("Test user created")
        
        # Get user ID for project creation
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        if user_result:
            user_id = user_result[0]
            print(f"Using user ID: {user_id}")
            
            # Check if we have projects
            cursor.execute("SELECT COUNT(*) FROM projects")
            project_count = cursor.fetchone()[0]
            
            if project_count == 0:
                print("Creating test project...")
                project_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO projects (id, name, description, target_domain, owner_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    'Test Website Scan',
                    'Test project for vulnerability scanning',
                    'https://example.com',
                    user_id,
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
                print(f"Test project created with ID: {project_id}")
        
        # Commit changes
        conn.commit()
        print("\n=== Database setup completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database_schema()