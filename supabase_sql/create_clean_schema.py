#!/usr/bin/env python3
"""
Create a clean version of combined_schema.sql for initial deployment.
This removes all DROP TRIGGER IF EXISTS statements that trigger Supabase's destructive operation warning.
"""

import re

def create_clean_schema():
    """Remove DROP TRIGGER statements for clean initial deployment"""
    
    # Read the original schema
    with open('combined_schema.sql', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all DROP TRIGGER IF EXISTS statements
    # Pattern matches: DROP TRIGGER IF EXISTS trigger_name ON table_name;
    drop_trigger_pattern = r'DROP TRIGGER IF EXISTS [^;]+;\n'
    
    # Count how many DROP statements we're removing
    drop_statements = re.findall(drop_trigger_pattern, content)
    drop_count = len(drop_statements)
    
    # Remove the DROP statements
    clean_content = re.sub(drop_trigger_pattern, '', content)
    
    # Add header comment explaining this is the clean version
    header_addition = """-- =====================================================
-- CLEAN VERSION FOR INITIAL DEPLOYMENT
-- =====================================================
-- This version removes all DROP TRIGGER statements to avoid
-- Supabase's "destructive operation" warning on fresh deployments.
-- Use combined_schema.sql for updates/re-deployments.
-- =====================================================

"""
    
    # Insert the header after the first comment block
    first_comment_end = clean_content.find('-- =====================================================', 1)
    if first_comment_end != -1:
        # Find the end of the first comment block
        next_section = clean_content.find('\n-- =====================================================', first_comment_end + 1)
        if next_section != -1:
            clean_content = (clean_content[:next_section] + 
                           '\n' + header_addition + 
                           clean_content[next_section:])
    
    # Write the clean version
    with open('combined_schema_clean.sql', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print("✅ Clean schema created: combined_schema_clean.sql")
    print(f"📊 Removed {drop_count} DROP TRIGGER statements")
    print(f"📁 File size: {len(clean_content):,} bytes")
    print("\n🚀 Use combined_schema_clean.sql for initial deployment")
    print("🔄 Use combined_schema.sql for updates/re-deployments")

if __name__ == "__main__":
    create_clean_schema()