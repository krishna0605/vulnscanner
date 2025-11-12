#!/usr/bin/env python3
"""Script to add @pytest.mark.asyncio decorators to async test methods."""

import re
from pathlib import Path

def fix_async_tests(file_path):
    """Add @pytest.mark.asyncio decorators to async test methods."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern removed; logic below handles decorator insertion via line scanning
    
    def replacement(match):
        indent = match.group(1)
        method_def = match.group(2)
        return f'{indent}@pytest.mark.asyncio{indent}{method_def}'
    
    # Only add decorator if it's not already there
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is an async test method
        if re.match(r'    async def test_', line):
            # Check if the previous line already has the decorator
            if i > 0 and '@pytest.mark.asyncio' in lines[i-1]:
                new_lines.append(line)
            else:
                # Add the decorator
                new_lines.append('    @pytest.mark.asyncio')
                new_lines.append(line)
        else:
            new_lines.append(line)
        
        i += 1
    
    new_content = '\n'.join(new_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed async tests in {file_path}")

def main():
    """Fix all integration test files."""
    test_dir = Path("tests/integration")
    
    for test_file in test_dir.glob("test_*.py"):
        fix_async_tests(test_file)

if __name__ == "__main__":
    main()