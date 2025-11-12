#!/usr/bin/env python3
"""
Debug script to check user IDs and ownership relationships.
"""
import sqlite3
import jwt
from pathlib import Path

def debug_ownership():
    """Debug ownership relationships."""
    db_path = Path("dev.db")
    
    if not db_path.exists():
        print(f"❌ Database file {db_path} does not exist")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check profiles table
        print("=== PROFILES TABLE ===")
        cursor.execute("SELECT id, username, full_name FROM profiles")
        profiles = cursor.fetchall()
        for profile in profiles:
            print(f"Profile: {profile}")
        
        # Check projects table
        print("\n=== PROJECTS TABLE ===")
        cursor.execute("SELECT id, name, owner_id FROM projects")
        projects = cursor.fetchall()
        for project in projects:
            print(f"Project: {project}")
        
        # Check scan_sessions table
        print("\n=== SCAN SESSIONS TABLE ===")
        cursor.execute("SELECT id, project_id, created_by FROM scan_sessions")
        scans = cursor.fetchall()
        for scan in scans:
            print(f"Scan: {scan}")
        
        # Check the specific scan and project relationship
        scan_id = "e39b35fa-8a14-4996-a4dd-2836f6e3c990"
        print(f"\n=== SCAN {scan_id} DETAILS ===")
        
        cursor.execute("""
            SELECT 
                s.id as scan_id,
                s.project_id,
                s.created_by as scan_created_by,
                p.id as project_id,
                p.owner_id as project_owner_id,
                p.name as project_name
            FROM scan_sessions s
            JOIN projects p ON s.project_id = p.id
            WHERE s.id = ?
        """, (scan_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"Scan ID: {result[0]}")
            print(f"Project ID: {result[1]}")
            print(f"Scan Created By: {result[2]}")
            print(f"Project Owner ID: {result[4]}")
            print(f"Project Name: {result[5]}")
            print(f"Match: {result[2] == result[4]}")
        else:
            print("No matching scan found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def decode_jwt_token():
    """Decode the JWT token to see what user_id it contains."""
    # This is the token from our last login
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NGY2Yzk2Yy1kNTI1LTRkYmQtOGE3YS03YTEwOTk1NTI2YjUiLCJleHAiOjE3NjE5OTQ0NzMsImlhdCI6MTc2MTk5MDg3MywiaXNzIjoidnVsbnNjYW5uZXItYXBpIiwiYXVkIjoidnVsbnNjYW5uZXItZnJvbnRlbmQiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlciJ9.q5fffVFK_yRXcjM-hDfUWXVr4My_4s6k2sL048kkmjk"
    
    try:
        # Decode without verification for debugging
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("\n=== JWT TOKEN CONTENTS ===")
        for key, value in decoded.items():
            print(f"{key}: {value}")
        
        user_id = decoded.get('sub')
        print(f"\nExtracted user_id: {user_id}")
        return user_id
        
    except Exception as e:
        print(f"❌ Error decoding JWT: {e}")
        return None

if __name__ == "__main__":
    debug_ownership()
    decode_jwt_token()