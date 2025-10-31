#!/usr/bin/env python3
"""
Database setup script for Enhanced Vulnerability Scanner
Applies the complete schema to Supabase PostgreSQL database
"""
import os
import sys
from pathlib import Path
from core.config import Settings

def setup_database():
    """Apply the database schema to Supabase."""
    try:
        print("🚀 Setting up database schema...")
        
        # Load settings
        settings = Settings()
        
        # Check configuration
        if not settings.supabase_url or not settings.supabase_service_role_key:
            print("❌ Supabase configuration missing")
            print(f"URL: {'✅' if settings.supabase_url else '❌'}")
            print(f"Service Key: {'✅' if settings.supabase_service_role_key else '❌'}")
            return False
        
        print(f"📡 Supabase URL: {settings.supabase_url}")
        
        # Read schema file
        schema_file = Path(__file__).parent.parent / "supabase_sql" / "combined_schema_clean.sql"
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        print(f"📄 Reading schema file: {schema_file}")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print(f"📊 Schema file size: {len(schema_sql)} characters")
        
        print("✅ Schema file loaded successfully!")
        print("💡 To apply the schema, please:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the schema from combined_schema_clean.sql")
        print("4. Execute the SQL")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🗄️  ENHANCED VULNERABILITY SCANNER - DATABASE SETUP")
    print("=" * 60)
    
    # Setup database schema
    schema_success = setup_database()
    
    if schema_success:
        print("\n" + "=" * 60)
        print("✅ DATABASE SETUP INSTRUCTIONS PROVIDED!")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("1. Apply the schema in Supabase dashboard")
        print("2. Test project creation API")
        print("3. Verify data storage")
        print("\n🔑 Development credentials:")
        print("Token: dev-bypass (development mode)")
        print("User ID: 1 (auto-assigned in dev mode)")
    else:
        print("\n❌ Database setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()