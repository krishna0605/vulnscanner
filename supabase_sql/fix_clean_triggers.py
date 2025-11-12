#!/usr/bin/env python3
"""
Fix trigger conflicts in combined_schema_clean.sql
This script adds DROP TRIGGER IF EXISTS before CREATE TRIGGER statements
to handle existing triggers gracefully.
"""

import re
import os

def fix_clean_triggers():
    """Add DROP TRIGGER IF EXISTS before CREATE TRIGGER statements"""
    
    file_path = 'combined_schema_clean.sql'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match CREATE TRIGGER statements with table detection
    # This will match: CREATE TRIGGER trigger_name ... ON table_name
    # Removed unused detailed trigger pattern to avoid lint warning
    
    def replace_trigger(match):
        trigger_name = match.group(1)
        table_name = match.group(2)
        
        # Add DROP TRIGGER IF EXISTS before CREATE TRIGGER
        return f'DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};\nCREATE TRIGGER {trigger_name}'
    
    # For triggers without explicit table (like auth.users), use a simpler pattern
    simple_trigger_pattern = r'CREATE TRIGGER\s+(\w+)'
    
    def replace_simple_trigger(match):
        trigger_name = match.group(1)
        # Removed unused variable assignment
        
        # Try to find the table name in the following lines
        remaining_text = content[match.end():]
        table_match = re.search(r'ON\s+([^\s]+)', remaining_text[:200])
        
        if table_match:
            table_name = table_match.group(1)
            return f'DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};\nCREATE TRIGGER {trigger_name}'
        else:
            # Fallback for auth triggers
            return f'DROP TRIGGER IF EXISTS {trigger_name};\nCREATE TRIGGER {trigger_name}'
    
    # Replace all CREATE TRIGGER statements
    modified_content = re.sub(simple_trigger_pattern, replace_simple_trigger, content)
    
    # Count the number of modifications
    drop_count = len(re.findall(r'DROP TRIGGER IF EXISTS', modified_content))
    
    # Write the modified content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"✅ Successfully added DROP TRIGGER IF EXISTS to {drop_count} triggers in {file_path}")
    print(f"📁 File size: {len(modified_content)} bytes")
    print("🔧 Added conditional trigger creation to avoid conflicts")
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing trigger conflicts in combined_schema_clean.sql...")
    success = fix_clean_triggers()
    
    if success:
        print("\n✅ Clean schema trigger conflicts fixed!")
        print("💡 The schema now handles existing triggers gracefully")
        print("📋 Safe for both initial deployments and updates")
    else:
        print("\n❌ Failed to fix trigger conflicts")