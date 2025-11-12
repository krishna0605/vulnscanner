#!/usr/bin/env python3
"""
Check the vulnscanner.db database tables and content.
"""
import sqlite3
from pathlib import Path

def check_database():
    """Check the dev.db database."""
    db_path = Path("dev.db")
    
    if not db_path.exists():
        print(f"❌ Database file {db_path} does not exist")
        return
    
    print(f"✅ Database file {db_path} exists")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Available tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check discovered_urls table specifically
        if any(table[0] == 'discovered_urls' for table in tables):
            print("\n✅ discovered_urls table exists")
            
            # Count total URLs
            cursor.execute("SELECT COUNT(*) FROM discovered_urls")
            total_count = cursor.fetchone()[0]
            print(f"📊 Total URLs in database: {total_count}")
            
            # Check for our specific scan session
            scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
            cursor.execute("SELECT COUNT(*) FROM discovered_urls WHERE session_id = ?", (scan_id,))
            scan_count = cursor.fetchone()[0]
            print(f"📊 URLs for scan {scan_id}: {scan_count}")
            
            # Show sample records if any exist
            cursor.execute("SELECT * FROM discovered_urls LIMIT 5")
            sample_records = cursor.fetchall()
            if sample_records:
                print("\n📝 Sample records:")
                for record in sample_records:
                    print(f"  {record}")
            else:
                print("\n📝 No URL records found")
        else:
            print("\n❌ discovered_urls table does not exist")
        
        # Check scan_sessions table
        if any(table[0] == 'scan_sessions' for table in tables):
            print("\n✅ scan_sessions table exists")
            
            cursor.execute("SELECT COUNT(*) FROM scan_sessions")
            session_count = cursor.fetchone()[0]
            print(f"📊 Total scan sessions: {session_count}")
            
            # Show our scan session
            scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
            cursor.execute("SELECT * FROM scan_sessions WHERE id = ?", (scan_id,))
            scan_record = cursor.fetchone()
            if scan_record:
                print(f"📝 Our scan session: {scan_record}")
            else:
                print(f"❌ Scan session {scan_id} not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()