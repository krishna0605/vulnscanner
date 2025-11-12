#!/usr/bin/env python3
"""Debug password hashing"""
from core.security import get_password_hash, verify_password

# Test password hashing
password = "testpassword123"
hash1 = get_password_hash(password)
print(f"Generated hash: {hash1}")
print(f"Hash length: {len(hash1)}")

# Test verification
result = verify_password(password, hash1)
print(f"Verification result: {result}")

# Test with wrong password
wrong_result = verify_password("wrongpassword", hash1)
print(f"Wrong password result: {wrong_result}")