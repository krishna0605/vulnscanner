#!/usr/bin/env python3
"""
Create a test JWT token for authentication testing.
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.security import create_access_token  # noqa: E402

def create_test_token():
    """Create a test JWT token."""
    print("🚀 Creating test JWT token...")
    
    # Use existing user ID from SQLite database (integer format)
    test_user_id = "1"  # Using user ID 1 from the existing database
    
    # Create access token (expires in 60 minutes by default)
    token = create_access_token(subject=test_user_id, expires_minutes=60)
    
    print("✅ Test JWT token created successfully!")
    print(f"👤 User ID: {test_user_id}")
    print(f"🔑 Token: {token}")
    print("⏰ Expires in: 60 minutes")
    print()
    print("📋 To test authentication, use this token in the Authorization header:")
    print(f"Authorization: Bearer {token}")
    print()
    print("🧪 Test with curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/projects')
    
    return token

if __name__ == "__main__":
    create_test_token()