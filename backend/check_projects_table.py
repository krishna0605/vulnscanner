#!/usr/bin/env python3
"""
Check Projects Table Structure and Data
Verifies that the projects table exists and has the correct structure
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection using Supabase connection string"""
    
    # Get Supabase URL and extract connection details
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url:
        print("❌ Missing SUPABASE_URL in .env file")
        return None
    
    # For direct database connection, we need the database URL
    # Supabase format: https://xxx.supabase.co
    # We need to construct the PostgreSQL connection string
    
    # Try to get direct database URL if available
    db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    
    if db_url:
        try:
            conn = psycopg2.connect(db_url)
            return conn
        except Exception as e:
            print(f"❌ Could not connect using DATABASE_URL: {e}")
    
    print("💡 Direct database connection not available.")
    print("📝 Please check your Supabase dashboard to verify tables exist.")
    return None

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = %s
    );
    """
    
    cursor.execute(query, (table_name,))
    return cursor.fetchone()[0]

def get_table_structure(cursor, table_name):
    """Get table structure information"""
    
    query = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = %s
    ORDER BY ordinal_position;
    """
    
    cursor.execute(query, (table_name,))
    return cursor.fetchall()

def count_records(cursor, table_name):
    """Count records in a table"""
    
    query = f"SELECT COUNT(*) FROM public.{table_name};"
    cursor.execute(query)
    return cursor.fetchone()[0]

def get_sample_projects(cursor):
    """Get sample project records"""
    
    query = """
    SELECT id, name, target_domain, owner_id, created_at
    FROM public.projects
    ORDER BY created_at DESC
    LIMIT 5;
    """
    
    cursor.execute(query)
    return cursor.fetchall()

def main():
    """Main function to check database tables"""
    
    print("🚀 Checking database tables...")
    
    # Try to connect to database
    conn = get_db_connection()
    
    if not conn:
        print("\n💡 Alternative verification methods:")
        print("1. Check your Supabase dashboard > Table Editor")
        print("2. Run SQL queries directly in Supabase SQL Editor")
        print("3. Use the Supabase client in your application")
        return
    
    try:
        cursor = conn.cursor()
        
        # Check users table
        print("\n🔍 Checking users table...")
        if check_table_exists(cursor, 'users'):
            print("✅ Users table exists!")
            
            # Get table structure
            structure = get_table_structure(cursor, 'users')
            print("📋 Users table structure:")
            for col in structure:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            # Count records
            count = count_records(cursor, 'users')
            print(f"👥 Total users: {count}")
            
        else:
            print("❌ Users table does not exist!")
        
        # Check projects table
        print("\n🔍 Checking projects table...")
        if check_table_exists(cursor, 'projects'):
            print("✅ Projects table exists!")
            
            # Get table structure
            structure = get_table_structure(cursor, 'projects')
            print("📋 Projects table structure:")
            for col in structure:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            # Count records
            count = count_records(cursor, 'projects')
            print(f"📊 Total projects: {count}")
            
            if count > 0:
                print("\n📋 Sample projects:")
                projects = get_sample_projects(cursor)
                for project in projects:
                    print(f"  - ID: {project[0]}")
                    print(f"    Name: {project[1]}")
                    print(f"    Domain: {project[2]}")
                    print(f"    Owner: {project[3]}")
                    print(f"    Created: {project[4]}")
                    print()
            else:
                print("📝 No projects found in database")
            
        else:
            print("❌ Projects table does not exist!")
            print("💡 You may need to apply the schema to your Supabase database")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()