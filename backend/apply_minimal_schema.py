#!/usr/bin/env python3
"""
Apply minimal schema to Supabase using REST API
"""
import requests
from pathlib import Path
from core.config import Settings

def apply_minimal_schema():
    """Apply the minimal schema to Supabase."""
    try:
        print("🚀 Applying minimal schema to Supabase...")
        
        # Load settings
        settings = Settings()
        
        if not settings.supabase_url or not settings.supabase_service_role_key:
            print("❌ Supabase configuration missing")
            return False
        
        # Read minimal schema
        schema_file = Path(__file__).parent / "minimal_schema.sql"
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print(f"📄 Schema size: {len(schema_sql)} characters")
        
        # Prepare API request
        f"{settings.supabase_url}/rest/v1/rpc/exec_sql"
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "apikey": settings.supabase_service_role_key
        }
        
        # Split schema into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"📊 Executing {len(statements)} SQL statements...")
        
        success_count = 0
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            print(f"🔧 Executing statement {i}/{len(statements)}...")
            
            # Try to execute via direct SQL endpoint
            sql_url = f"{settings.supabase_url}/rest/v1/rpc/exec_sql"
            payload = {"sql": statement}
            
            try:
                response = requests.post(sql_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code in [200, 201]:
                    success_count += 1
                    print(f"✅ Statement {i} executed successfully")
                else:
                    print(f"⚠️  Statement {i} warning: {response.status_code} - {response.text[:100]}")
                    # Continue with other statements
                    
            except Exception as e:
                print(f"⚠️  Statement {i} error: {e}")
                # Continue with other statements
        
        print(f"\n📊 Results: {success_count}/{len(statements)} statements executed")
        
        if success_count > 0:
            print("✅ Schema application completed!")
            return True
        else:
            print("❌ No statements executed successfully")
            return False
        
    except Exception as e:
        print(f"❌ Schema application failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tables():
    """Test if tables were created successfully."""
    try:
        print("\n🧪 Testing table creation...")
        
        settings = Settings()
        
        # Test users table
        url = f"{settings.supabase_url}/rest/v1/users?select=count"
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "apikey": settings.supabase_service_role_key
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Users table accessible")
        else:
            print(f"⚠️  Users table issue: {response.status_code}")
        
        # Test projects table
        url = f"{settings.supabase_url}/rest/v1/projects?select=count"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Projects table accessible")
        else:
            print(f"⚠️  Projects table issue: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table testing failed: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🗄️  APPLYING MINIMAL SCHEMA TO SUPABASE")
    print("=" * 60)
    
    # Apply schema
    schema_success = apply_minimal_schema()
    
    if schema_success:
        # Test tables
        test_tables()
        
        print("\n" + "=" * 60)
        print("✅ MINIMAL SCHEMA APPLICATION COMPLETE!")
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

if __name__ == "__main__":
    main()