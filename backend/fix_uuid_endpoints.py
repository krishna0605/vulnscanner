#!/usr/bin/env python3
"""
Script to apply UUID to string conversion fix to all endpoints in scan_results.py
"""

import re

def fix_scan_results_endpoints():
    """Apply UUID conversion fix to all endpoints in scan_results.py"""
    
    file_path = "api/routes/scan_results.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match function definitions with scan_id: UUID parameter
    function_pattern = r'(async def \w+\(\s*scan_id: UUID[^)]*\):[^{]*?"""[^"]*?"""[^{]*?try:)'
    
    # Pattern to match ScanSession.id == scan_id (not already converted)
    scan_session_pattern = r'ScanSession\.id\s*==\s*scan_id(?!_str)'
    
    # Pattern to match DiscoveredUrl.session_id == scan_id (not already converted)
    discovered_url_pattern = r'DiscoveredUrl\.session_id\s*==\s*scan_id(?!_str)'
    
    # Pattern to match ExtractedForm.session_id == scan_id (not already converted)
    extracted_form_pattern = r'ExtractedForm\.session_id\s*==\s*scan_id(?!_str)'
    
    # Pattern to match TechnologyFingerprint.session_id == scan_id (not already converted)
    tech_fingerprint_pattern = r'TechnologyFingerprint\.session_id\s*==\s*scan_id(?!_str)'
    
    # Pattern to match session_id=scan_id in object creation (not already converted)
    session_id_assignment_pattern = r'session_id\s*=\s*scan_id(?!_str)'
    
    # Find all function definitions and add UUID conversion
    def add_uuid_conversion(match):
        func_def = match.group(1)
        if 'scan_id_str = str(scan_id)' not in func_def:
            # Add UUID conversion after the try: statement
            func_def = func_def.replace('try:', 'try:\n        # Convert UUID to string for SQLite compatibility\n        scan_id_str = str(scan_id)\n        ')
        return func_def
    
    # Apply UUID conversion to function definitions
    content = re.sub(function_pattern, add_uuid_conversion, content, flags=re.DOTALL)
    
    # Replace all scan_id references with scan_id_str
    content = re.sub(scan_session_pattern, 'ScanSession.id == scan_id_str', content)
    content = re.sub(discovered_url_pattern, 'DiscoveredUrl.session_id == scan_id_str', content)
    content = re.sub(extracted_form_pattern, 'ExtractedForm.session_id == scan_id_str', content)
    content = re.sub(tech_fingerprint_pattern, 'TechnologyFingerprint.session_id == scan_id_str', content)
    content = re.sub(session_id_assignment_pattern, 'session_id=scan_id_str', content)
    
    # Write the updated content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("UUID conversion fix applied to all endpoints in scan_results.py")

if __name__ == "__main__":
    fix_scan_results_endpoints()