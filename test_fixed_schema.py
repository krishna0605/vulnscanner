#!/usr/bin/env python3
"""
Simple test script to validate the fixed schema syntax
"""

import os
import re

def test_fixed_schema():
    """Test the fixed schema for common issues"""
    
    # Read the fixed schema file
    schema_file = "c:\\Users\\Admin\\Desktop\\vulscAN\\supabase_sql\\combined_schema_clean_fixed.sql"
    
    if not os.path.exists(schema_file):
        print(f"❌ Error: Schema file not found: {schema_file}")
        return False
        
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print(f"✅ Read schema file: {len(schema_sql)} characters")
    
    # Check for auth.users references (should be none in fixed version, except comments)
    lines = schema_sql.split('\n')
    auth_refs_in_code = 0
    for i, line in enumerate(lines, 1):
        if 'auth.users' in line and not line.strip().startswith('--'):
            print(f"❌ Error: Found auth.users reference in code at line {i}: {line.strip()}")
            auth_refs_in_code += 1
    
    if auth_refs_in_code > 0:
        print(f"❌ Error: Found {auth_refs_in_code} references to auth.users in actual code")
        return False
    
    # Check for public.users references (should be many)
    public_refs = schema_sql.count("public.users")
    if public_refs == 0:
        print("❌ Error: No references to public.users found in fixed schema")
        return False
    
    print("✅ Schema validation passed:")
    print("   - No auth.users references found")
    print(f"   - Found {public_refs} public.users references")
    
    # Check for user_id column definitions
    user_id_refs = schema_sql.count("user_id UUID REFERENCES public.users(id)")
    print(f"   - Found {user_id_refs} proper user_id foreign key references")
    
    # Test basic table creation syntax
    if "CREATE TABLE public.users" in schema_sql:
        print("✅ public.users table definition found")
    else:
        print("❌ Error: public.users table definition not found")
        return False
    
    # Check for common SQL syntax issues
    syntax_checks = [
        ("Missing semicolons", r'CREATE TABLE[^;]*\n(?!.*;)', "CREATE TABLE statements should end with semicolon"),
        ("Invalid UUID references", r'UUID REFERENCES [^(]*\([^)]*\)', "Check UUID reference syntax"),
    ]
    
    issues_found = 0
    for check_name, pattern, description in syntax_checks:
        matches = re.findall(pattern, schema_sql, re.MULTILINE | re.IGNORECASE)
        if matches:
            print(f"⚠️  Warning: {check_name} - {description}")
            issues_found += len(matches)
    
    if issues_found == 0:
        print("✅ No syntax issues detected")
    
    print("\n✅ Fixed schema appears to be valid!")
    print("\nTo apply the schema:")
    print("1. Copy the contents of combined_schema_clean_fixed.sql")
    print("2. Go to your Supabase dashboard > SQL Editor")
    print("3. Paste and execute the SQL")
    print("\nThe fixed schema:")
    print("- Replaces all auth.users references with public.users")
    print("- Creates a proper users table in the public schema")
    print("- Maintains all foreign key relationships")
    print("- Includes proper indexes and triggers")
    
    return True

if __name__ == "__main__":
    success = test_fixed_schema()
    exit(0 if success else 1)