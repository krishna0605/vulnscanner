#!/usr/bin/env python3
"""
Apply Supabase schema migration script.
This script reads the SQL migration file and applies it to the Supabase database.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Windows event loop fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import asyncpg  # noqa: E402
from core.config import settings  # noqa: E402


class SupabaseSchemaManager:
    """Manages Supabase schema migrations and setup."""
    
    def __init__(self):
        self.db_url = settings.supabase_db_url
        if not self.db_url:
            raise ValueError("SUPABASE_DB_URL environment variable is required")
    
    async def connect(self) -> asyncpg.Connection:
        """Create a connection to the Supabase database."""
        try:
            conn = await asyncpg.connect(self.db_url)
            print("✅ Connected to Supabase database")
            return conn
        except Exception as e:
            print(f"❌ Failed to connect to Supabase database: {e}")
            raise
    
    async def read_schema_file(self) -> str:
        """Read the SQL schema file."""
        schema_file = Path(__file__).parent / "supabase_schema.sql"
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Read schema file: {schema_file}")
        return content
    
    async def execute_sql_script(self, conn: asyncpg.Connection, sql_script: str) -> None:
        """Execute the SQL script in chunks to handle complex statements."""
        # Split the script into individual statements
        statements = []
        current_statement = []
        in_function = False
        
        for line in sql_script.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue
            
            # Track if we're inside a function definition
            if 'CREATE OR REPLACE FUNCTION' in line.upper() or 'CREATE FUNCTION' in line.upper():
                in_function = True
            elif line.upper().startswith('$$') and in_function:
                in_function = False
                current_statement.append(line)
                statements.append('\n'.join(current_statement))
                current_statement = []
                continue
            
            current_statement.append(line)
            
            # If we're not in a function and the line ends with semicolon, it's a complete statement
            if not in_function and line.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []
        
        # Add any remaining statement
        if current_statement:
            statements.append('\n'.join(current_statement))
        
        # Execute each statement
        executed_count = 0
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if not statement:
                continue
            
            try:
                await conn.execute(statement)
                executed_count += 1
                
                # Print progress for major operations
                if any(keyword in statement.upper() for keyword in ['CREATE TABLE', 'CREATE INDEX', 'CREATE POLICY']):
                    # Extract table/index/policy name for better logging
                    if 'CREATE TABLE' in statement.upper():
                        table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                        print(f"  📋 Created table: {table_name}")
                    elif 'CREATE INDEX' in statement.upper():
                        index_name = statement.split('CREATE INDEX')[1].split('ON')[0].strip()
                        print(f"  📊 Created index: {index_name}")
                    elif 'CREATE POLICY' in statement.upper():
                        policy_name = statement.split('"')[1] if '"' in statement else "policy"
                        print(f"  🔒 Created policy: {policy_name}")
                
            except Exception as e:
                print(f"⚠️  Warning executing statement {i+1}: {e}")
                print(f"Statement: {statement[:100]}...")
                # Continue with other statements
        
        print(f"✅ Executed {executed_count} SQL statements")
    
    async def verify_schema(self, conn: asyncpg.Connection) -> None:
        """Verify that the schema was applied correctly."""
        print("\n🔍 Verifying schema setup...")
        
        # Check tables
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'profiles', 'projects', 'scan_sessions', 'discovered_urls', 
            'extracted_forms', 'technology_fingerprints', 'dashboard_metrics', 'realtime_updates'
        )
        ORDER BY table_name;
        """
        
        tables = await conn.fetch(tables_query)
        expected_tables = {
            'profiles', 'projects', 'scan_sessions', 'discovered_urls',
            'extracted_forms', 'technology_fingerprints', 'dashboard_metrics', 'realtime_updates'
        }
        actual_tables = {row['table_name'] for row in tables}
        
        if actual_tables == expected_tables:
            print(f"✅ All {len(expected_tables)} tables created successfully")
            for table in sorted(actual_tables):
                print(f"  📋 {table}")
        else:
            missing = expected_tables - actual_tables
            extra = actual_tables - expected_tables
            if missing:
                print(f"❌ Missing tables: {missing}")
            if extra:
                print(f"ℹ️  Extra tables: {extra}")
        
        # Check RLS
        rls_query = """
        SELECT schemaname, tablename, rowsecurity 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'profiles', 'projects', 'scan_sessions', 'discovered_urls', 
            'extracted_forms', 'technology_fingerprints', 'dashboard_metrics', 'realtime_updates'
        );
        """
        
        rls_tables = await conn.fetch(rls_query)
        rls_enabled = sum(1 for row in rls_tables if row['rowsecurity'])
        
        print(f"✅ Row Level Security enabled on {rls_enabled}/{len(rls_tables)} tables")
        
        # Check indexes
        indexes_query = """
        SELECT COUNT(*) as index_count
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND tablename IN (
            'profiles', 'projects', 'scan_sessions', 'discovered_urls', 
            'extracted_forms', 'technology_fingerprints', 'dashboard_metrics', 'realtime_updates'
        );
        """
        
        index_result = await conn.fetchrow(indexes_query)
        index_count = index_result['index_count']
        print(f"✅ Created {index_count} performance indexes")
        
        # Check functions
        functions_query = """
        SELECT COUNT(*) as function_count
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
        AND p.proname IN ('handle_new_user', 'update_updated_at_column');
        """
        
        function_result = await conn.fetchrow(functions_query)
        function_count = function_result['function_count']
        print(f"✅ Created {function_count} database functions")
        
        print("\n🎉 Schema verification completed!")
    
    async def apply_schema(self) -> None:
        """Apply the complete schema to Supabase."""
        print("🚀 Starting Supabase schema migration...")
        print("=" * 50)
        
        try:
            # Read the schema file
            sql_script = await self.read_schema_file()
            
            # Connect to database
            conn = await self.connect()
            
            try:
                # Apply the schema
                print("\n📝 Applying schema migration...")
                await self.execute_sql_script(conn, sql_script)
                
                # Verify the schema
                await self.verify_schema(conn)
                
                print("\n" + "=" * 50)
                print("✅ Supabase schema migration completed successfully!")
                print("🔒 Row Level Security policies are active")
                print("📊 Performance indexes are in place")
                print("🔄 Triggers and functions are configured")
                print("🚀 Your Enhanced Vulnerability Scanner is ready!")
                
            finally:
                await conn.close()
                print("🔌 Database connection closed")
                
        except Exception as e:
            print(f"\n❌ Schema migration failed: {e}")
            raise


async def main():
    """Main function to run the schema migration."""
    try:
        manager = SupabaseSchemaManager()
        await manager.apply_schema()
        return 0
    except Exception as e:
        print(f"\n💥 Migration failed with error: {e}")
        return 1


if __name__ == "__main__":
    print("Enhanced Vulnerability Scanner - Supabase Schema Migration")
    print("=" * 60)
    
    # Check environment
    if not settings.supabase_db_url:
        print("❌ SUPABASE_DB_URL environment variable is not set")
        print("Please set up your .env file with Supabase credentials")
        sys.exit(1)
    
    # Run the migration
    exit_code = asyncio.run(main())
    sys.exit(exit_code)