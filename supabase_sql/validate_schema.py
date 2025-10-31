#!/usr/bin/env python3
"""
Simple SQL schema validation script for the combined schema file.
Checks for basic syntax issues and common problems.
"""

import re
import sys
from pathlib import Path

def validate_sql_file(file_path):
    """Validate SQL file for basic syntax issues."""
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading file: {e}"], []
    
    lines = content.split('\n')
    
    # Check for common syntax issues
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Skip comments and empty lines
        if not line_stripped or line_stripped.startswith('--'):
            continue
            
        # Check for reserved keywords used as column names (without quotes)
        reserved_keywords = ['references', 'constraint', 'table', 'index', 'view', 'function', 'trigger', 'type', 'schema', 'database', 'user', 'grant', 'revoke']
        for keyword in reserved_keywords:
            # Look for pattern: whitespace + keyword + whitespace + type/constraint
            pattern = rf'\s+{keyword}\s+\w+.*DEFAULT'
            if re.search(pattern, line, re.IGNORECASE):
                if keyword == 'references':
                    errors.append(f"Line {i}: Reserved keyword '{keyword}' used as column name: {line_stripped}")
                else:
                    warnings.append(f"Line {i}: Reserved keyword '{keyword}' used as column name (may cause issues): {line_stripped}")
        
        # Check for unmatched parentheses in CREATE statements
        if line_stripped.upper().startswith('CREATE'):
            open_parens = line.count('(')
            close_parens = line.count(')')
            if open_parens != close_parens and open_parens > 0:
                # This is expected for multi-line CREATE statements
                pass
        
        # Check for missing semicolons at end of statements
        if (line_stripped.upper().startswith(('CREATE', 'INSERT', 'UPDATE', 'DELETE', 'ALTER', 'DROP')) and 
            not line_stripped.endswith(';') and 
            not line_stripped.endswith('$$') and
            '(' not in line_stripped):
            warnings.append(f"Line {i}: Statement may be missing semicolon: {line_stripped}")
    
    # Check for balanced parentheses in the entire file
    open_count = content.count('(')
    close_count = content.count(')')
    if open_count != close_count:
        errors.append(f"Unbalanced parentheses: {open_count} opening, {close_count} closing")
    
    # Check for balanced quotes
    single_quotes = content.count("'")
    if single_quotes % 2 != 0:
        warnings.append(f"Potentially unbalanced single quotes: {single_quotes} total")
    
    return errors, warnings

def main():
    schema_file = Path(__file__).parent / 'combined_schema.sql'
    
    if not schema_file.exists():
        print(f"Error: Schema file not found: {schema_file}")
        sys.exit(1)
    
    print(f"Validating SQL schema: {schema_file}")
    print("=" * 50)
    
    errors, warnings = validate_sql_file(schema_file)
    
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  ❌ {error}")
        print()
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ No syntax issues found!")
    elif not errors:
        print("✅ No critical errors found (only warnings)")
    else:
        print("❌ Critical errors found - please fix before deployment")
        sys.exit(1)
    
    print(f"\nValidation complete. File size: {schema_file.stat().st_size:,} bytes")

if __name__ == "__main__":
    main()