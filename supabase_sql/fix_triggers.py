#!/usr/bin/env python3
"""
Script to fix trigger conflicts in combined_schema.sql by adding DROP TRIGGER IF EXISTS statements
"""

import re
import os

def fix_triggers_in_file(file_path):
    """Add DROP TRIGGER IF EXISTS before each CREATE TRIGGER statement"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match CREATE TRIGGER statements
    # This will match: CREATE TRIGGER trigger_name
    trigger_pattern = r'CREATE TRIGGER\s+(\w+)'
    
    def replace_trigger(match):
        trigger_name = match.group(1)
        # Extract the table name from the trigger context
        # Look for "ON table_name" pattern after the trigger name
        full_match = match.group(0)
        
        # Find the complete trigger statement to extract table name
        start_pos = match.start()
        # Look for the line containing "ON table_name"
        lines_after = content[start_pos:start_pos + 500].split('\n')
        table_name = None
        
        for line in lines_after:
            on_match = re.search(r'ON\s+([\w.]+)', line)
            if on_match:
                table_name = on_match.group(1)
                break
        
        if table_name:
            return f'DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};\nCREATE TRIGGER {trigger_name}'
        else:
            # Fallback: just add DROP without table specification (PostgreSQL will handle it)
            return f'DROP TRIGGER IF EXISTS {trigger_name};\nCREATE TRIGGER {trigger_name}'
    
    # Replace all CREATE TRIGGER statements
    modified_content = re.sub(trigger_pattern, replace_trigger, content)
    
    # Write the modified content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Fixed triggers in {file_path}")
    
    # Count how many triggers were modified
    trigger_count = len(re.findall(trigger_pattern, content))
    print(f"Modified {trigger_count} trigger statements")

if __name__ == "__main__":
    schema_file = "combined_schema.sql"
    
    if os.path.exists(schema_file):
        fix_triggers_in_file(schema_file)
        print("✅ Trigger conflicts fixed successfully!")
    else:
        print(f"❌ File {schema_file} not found")