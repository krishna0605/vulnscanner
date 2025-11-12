#!/usr/bin/env python3
"""
Generate secure random keys for VulnScanner environment configuration.
Run this script to generate new secure keys for production deployment.
"""

import secrets
import string
from datetime import datetime

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(length)

def generate_csrf_secret(length: int = 32) -> str:
    """Generate a secure CSRF secret."""
    return secrets.token_hex(length)

def generate_jwt_secret(length: int = 64) -> str:
    """Generate a secure JWT secret key."""
    return secrets.token_urlsafe(length)

def generate_api_key(length: int = 32) -> str:
    """Generate a secure API key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    """Generate and display secure keys."""
    print("=" * 80)
    print("VulnScanner Secure Key Generator")
    print(f"Generated on: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    print("# Copy these values to your .env file:")
    print()
    
    print("# Application Security")
    print(f"SECRET_KEY={generate_secret_key()}")
    print(f"JWT_SECRET_KEY={generate_jwt_secret()}")
    print(f"CSRF_SECRET={generate_csrf_secret()}")
    print()
    
    print("# API Keys")
    print(f"API_KEY={generate_api_key()}")
    print()
    
    print("# Session Security")
    print(f"SESSION_SECRET={generate_secret_key()}")
    print()
    
    print("=" * 80)
    print("IMPORTANT SECURITY NOTES:")
    print("1. Keep these keys secret and secure")
    print("2. Use different keys for different environments")
    print("3. Rotate keys regularly in production")
    print("4. Never commit these keys to version control")
    print("=" * 80)

if __name__ == "__main__":
    main()