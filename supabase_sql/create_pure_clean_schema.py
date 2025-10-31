#!/usr/bin/env python3
"""
Create a pure clean schema for initial Supabase deployment
This script removes ALL DROP statements to avoid any "destructive operation" warnings.
"""

import re
import os

def create_pure_clean_schema():
    """Create a completely clean schema without any DROP statements"""
    
    source_file = 'combined_schema.sql'
    output_file = 'combined_schema_initial.sql'
    
    if not os.path.exists(source_file):
        print(f"Error: {source_file} not found!")
        return False
    
    # Read the source file
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all DROP statements (triggers, functions, etc.)
    patterns_to_remove = [
        r'DROP TRIGGER IF EXISTS[^;]*;[\s]*\n?',
        r'DROP FUNCTION IF EXISTS[^;]*;[\s]*\n?',
        r'DROP VIEW IF EXISTS[^;]*;[\s]*\n?',
        r'DROP INDEX IF EXISTS[^;]*;[\s]*\n?',
        r'DROP TABLE IF EXISTS[^;]*;[\s]*\n?',
        r'DROP TYPE IF EXISTS[^;]*;[\s]*\n?',
        r'DROP POLICY IF EXISTS[^;]*;[\s]*\n?',
        r'DROP CONSTRAINT IF EXISTS[^;]*;[\s]*\n?'
    ]
    
    modified_content = content
    total_removed = 0
    
    for pattern in patterns_to_remove:
        matches = re.findall(pattern, modified_content, re.IGNORECASE | re.MULTILINE)
        total_removed += len(matches)
        modified_content = re.sub(pattern, '', modified_content, flags=re.IGNORECASE | re.MULTILINE)
    
    # Clean up multiple consecutive newlines
    modified_content = re.sub(r'\n\s*\n\s*\n', '\n\n', modified_content)
    
    # Update the header comment
    header_replacement = """-- =====================================================
-- ENHANCED VULNERABILITY SCANNER - COMPLETE SCHEMA
-- =====================================================
-- Combined schema file for Supabase PostgreSQL database
-- This file combines all schema components in proper execution order
-- 
-- Execution Order:
-- 1. Extensions and Types
-- 2. Core Tables (Users, Auth, System)
-- 3. Project Tables
-- 4. Scanning Tables
-- 5. Vulnerability Tables
-- 6. Reporting Tables
-- 7. Integration Tables
-- 8. Row Level Security Policies
-- 9. Indexes and Constraints
-- 10. Security Fixes
-- =====================================================
-- PURE CLEAN VERSION FOR INITIAL DEPLOYMENT
-- =====================================================
-- This version removes ALL DROP statements to completely avoid
-- Supabase's "destructive operation" warning on fresh deployments.
-- 
-- IMPORTANT: Use this ONLY for initial deployment on fresh databases.
-- For updates/re-deployments, use combined_schema.sql instead.
-- ====================================================="""
    
    # Replace the header
    modified_content = re.sub(
        r'-- =====================================================.*?-- =====================================================',
        header_replacement,
        modified_content,
        flags=re.DOTALL
    )
    
    # Write the pure clean version
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"✅ Successfully created {output_file}")
    print(f"📁 File size: {len(modified_content):,} bytes")
    print(f"🗑️  Removed {total_removed} DROP statements")
    print(f"🚀 Ready for initial Supabase deployment without warnings")
    
    return True

if __name__ == "__main__":
    print("🔧 Creating pure clean schema for initial deployment...")
    success = create_pure_clean_schema()
    
    if success:
        print("\n✅ Pure clean schema created successfully!")
        print("💡 Use combined_schema_initial.sql for fresh Supabase deployments")
        print("📋 No destructive operations - no warnings expected")
    else:
        print("\n❌ Failed to create pure clean schema")