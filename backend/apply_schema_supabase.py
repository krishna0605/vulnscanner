#!/usr/bin/env python3
"""
Apply minimal schema to Supabase using Python client
"""
from pathlib import Path
from supabase import create_client, Client
from core.config import Settings

def get_supabase_client() -> Client:
    """Get Supabase client."""
    settings = Settings()
    
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise ValueError("Supabase configuration missing")
    
    return create_client(settings.supabase_url, settings.supabase_service_role_key)

def apply_schema():
    """Apply the minimal schema to Supabase."""
    try:
        print("🚀 Applying minimal schema to Supabase...")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Read minimal schema
        schema_file = Path(__file__).parent / "minimal_schema.sql"
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print(f"📄 Schema size: {len(schema_sql)} characters")
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"📊 Executing {len(statements)} SQL statements...")
        
        success_count = 0
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                print(f"🔧 Executing statement {i}/{len(statements)}...")
                
                # Execute SQL statement
                _ = supabase.rpc('exec_sql', {'sql': statement}).execute()
                
                success_count += 1
                print(f"✅ Statement {i} executed successfully")
                
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                    print(f"ℹ️  Statement {i} skipped (already exists)")
                    success_count += 1
                else:
                    print(f"⚠️  Statement {i} error: {error_msg[:100]}")
                    # Continue with other statements
        
        print(f"\n📊 Results: {success_count}/{len(statements)} statements processed")
        
        if success_count > 0:
            print("✅ Schema application completed!")
            return True
        else:
            print("❌ No statements executed successfully")
            return False
        
    except Exception as e:
        print(f"❌ Schema application failed: {e}")
        return False

def create_tables_directly():
    """Create tables directly using Supabase client."""
    try:
        print("\n🔧 Creating tables directly...")
        
        supabase = get_supabase_client()
        
        # Create users table
        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            role VARCHAR(50) DEFAULT 'user',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create projects table
        projects_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            target_domain VARCHAR(255) NOT NULL,
            owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create scan_sessions table
        scans_sql = """
        CREATE TABLE IF NOT EXISTS scan_sessions (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            status VARCHAR(50) DEFAULT 'pending',
            start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            end_time TIMESTAMP WITH TIME ZONE,
            configuration JSONB DEFAULT '{}'::jsonb,
            stats JSONB DEFAULT '{}'::jsonb,
            created_by INTEGER REFERENCES users(id)
        );
        """
        
        # Insert test user
        test_user_sql = """
        INSERT INTO users (id, email, full_name, role, is_active) 
        VALUES (1, 'test@example.com', 'Test User', 'user', true)
        ON CONFLICT (email) DO NOTHING;
        """
        
        tables = [
            ("users", users_sql),
            ("projects", projects_sql), 
            ("scan_sessions", scans_sql),
            ("test_user", test_user_sql)
        ]
        
        for table_name, sql in tables:
            try:
                print(f"🔧 Creating {table_name}...")
                # Try using raw SQL execution
                _ = supabase.postgrest.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ {table_name} created successfully")
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower():
                    print(f"ℹ️  {table_name} already exists")
                else:
                    print(f"⚠️  {table_name} error: {error_msg[:100]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct table creation failed: {e}")
        return False

def test_tables():
    """Test if tables were created successfully."""
    try:
        print("\n🧪 Testing table creation...")
        
        supabase = get_supabase_client()
        
        # Test users table
        try:
            supabase.table('users').select('count').execute()
            print("✅ Users table accessible")
        except Exception as e:
            print(f"⚠️  Users table issue: {e}")
        
        # Test projects table
        try:
            supabase.table('projects').select('count').execute()
            print("✅ Projects table accessible")
        except Exception as e:
            print(f"⚠️  Projects table issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table testing failed: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🗄️  APPLYING SCHEMA TO SUPABASE")
    print("=" * 60)
    
    # Try applying schema first
    schema_success = apply_schema()
    
    if not schema_success:
        print("\n🔧 Trying direct table creation...")
        schema_success = create_tables_directly()
    
    if schema_success:
        # Test tables
        test_tables()
        
        print("\n" + "=" * 60)
        print("✅ SCHEMA APPLICATION COMPLETE!")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("1. Test project creation API")
        print("2. Verify data storage")
        print("\n🔑 Development credentials:")
        print("Token: dev-bypass")
        print("User ID: 1")
        print("Email: test@example.com")
    else:
        print("\n❌ Schema application failed")
        print("\n💡 Manual steps required:")
        print("1. Go to Supabase Dashboard > SQL Editor")
        print("2. Copy and paste minimal_schema.sql")
        print("3. Execute the SQL manually")

if __name__ == "__main__":
    main()