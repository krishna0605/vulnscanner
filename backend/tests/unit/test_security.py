"""
Unit tests for core.security module.
Tests password hashing, JWT token operations, and authentication functions.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from jose import jwt, JWTError
from fastapi import HTTPException

from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    verify_supabase_jwt,
    pwd_context
)
from core.config import settings


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50  # Hashed passwords should be long
        assert hashed.startswith("$pbkdf2-sha256$")  # PBKDF2 format
    
    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_empty_password_handling(self):
        """Test handling of empty passwords."""
        with pytest.raises(ValueError):
            get_password_hash("")
    
    def test_none_password_handling(self):
        """Test handling of None passwords."""
        with pytest.raises((ValueError, TypeError)):
            get_password_hash(None)
    
    def test_unicode_password_support(self):
        """Test support for Unicode passwords."""
        password = "тест_пароль_123_🔒"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_long_password_support(self):
        """Test support for long passwords."""
        password = "a" * 1000  # Very long password
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long
        
        # Verify token structure (header.payload.signature)
        parts = token.split(".")
        assert len(parts) == 3
    
    def test_create_token_with_expiration(self):
        """Test token creation with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        # Decode without verification to check expiration
        decoded = jwt.decode(token, key="", options={"verify_signature": False})
        
        # Check that expiration is set
        assert "exp" in decoded
        
        # Check that expiration is approximately 15 minutes from now
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = exp_time - now
        
        # Should be close to 15 minutes (allow 1 minute tolerance)
        assert 14 * 60 <= time_diff.total_seconds() <= 16 * 60
    
    def test_verify_valid_token(self):
        """Test verification of valid token."""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_expired_token(self):
        """Test verification of expired token."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)
        
        payload = verify_token(token)
        assert payload is None
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_verify_malformed_token(self):
        """Test verification of malformed token."""
        malformed_tokens = [
            "not.a.token",
            "too.few.parts",
            "too.many.parts.here.extra",
            "",
            "single_string_no_dots"
        ]
        
        for token in malformed_tokens:
            payload = verify_token(token)
            assert payload is None
    
    def test_token_with_additional_claims(self):
        """Test token with additional custom claims."""
        data = {
            "sub": "test@example.com",
            "user_id": "123",
            "role": "admin",
            "permissions": ["read", "write"],
            "custom_field": "custom_value"
        }
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]
        assert payload["custom_field"] == "custom_value"
    
    def test_token_algorithm_verification(self):
        """Test that tokens use the correct algorithm."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Decode header to check algorithm
        header = jwt.get_unverified_header(token)
        assert header["alg"] == settings.jwt_algorithm


class TestSupabaseJWT:
    """Test Supabase JWT verification."""
    
    @pytest.mark.asyncio
    async def test_verify_supabase_jwt_success(self):
        """Test successful Supabase JWT verification."""
        # Create a mock token
        token = "mock.jwt.token"
        
        with patch('jose.jwt.get_unverified_header') as mock_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_header.return_value = {"alg": "HS256", "typ": "JWT"}
            mock_decode.return_value = {
                "sub": "user-id",
                "email": "test@example.com",
                "aud": "authenticated",
                "exp": (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
            }
            
            result = await verify_supabase_jwt(token)
            
            assert result is not None
            assert result["sub"] == "user-id"
            assert result["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_verify_supabase_jwt_invalid_token(self):
        """Test Supabase JWT verification with invalid token."""
        # Test with invalid token that causes JWTError
        with patch('jose.jwt.get_unverified_header') as mock_header:
            mock_header.side_effect = JWTError("Invalid token format")
            
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_jwt("invalid.jwt.token")
            
            assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_verify_supabase_jwt_jwks_error(self):
        """Test Supabase JWT verification with decode error."""
        # Test with decode error
        with patch('jose.jwt.get_unverified_header') as mock_header, \
             patch('jose.jwt.decode') as mock_decode:
            
            mock_header.return_value = {"alg": "HS256", "typ": "JWT"}
            mock_decode.side_effect = Exception("Decode failed")
            
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_jwt("test.jwt.token")
            
            assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_verify_supabase_jwt_empty_token(self):
        """Test Supabase JWT verification with empty token."""
        # Empty token should cause JWT header parsing to fail
        with patch('jose.jwt.get_unverified_header') as mock_header:
            mock_header.side_effect = JWTError("Empty token")
            
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_jwt("")
            
            assert exc_info.value.status_code == 401


class TestPasswordContext:
    """Test password context configuration."""
    
    def test_password_context_schemes(self):
        """Test that password context uses correct schemes."""
        assert "pbkdf2_sha256" in pwd_context.schemes()
    
    def test_password_context_deprecated(self):
        """Test deprecated schemes handling."""
        # Should handle deprecated schemes gracefully
        # Check that context has schemes configured
        assert len(pwd_context.schemes()) > 0
    
    def test_password_rounds_configuration(self):
        """Test password hashing rounds configuration."""
        password = "test_password"
        hash1 = pwd_context.hash(password)
        
        # Verify the hash format includes rounds information
        assert "$pbkdf2-sha256$" in hash1
        
        # Verify password can be verified
        assert pwd_context.verify(password, hash1) is True


class TestSecurityHelpers:
    """Test security helper functions."""
    
    def test_token_expiration_calculation(self):
        """Test token expiration calculation."""
        # Test default expiration
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        payload = verify_token(token)
        
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = exp_time - now
        
        # Should be close to default expiration time
        expected_minutes = settings.jwt_exp_minutes
        expected_seconds = expected_minutes * 60
        
        # Allow 1 minute tolerance
        assert (expected_seconds - 60) <= time_diff.total_seconds() <= (expected_seconds + 60)
    
    def test_token_issued_at_claim(self):
        """Test that tokens include issued at claim."""
        data = {"sub": "test@example.com"}
        before_creation = datetime.now(timezone.utc)
        token = create_access_token(data)
        after_creation = datetime.now(timezone.utc)
        
        payload = verify_token(token)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        
        # Issued at time should be between before and after creation
        assert before_creation <= iat_time <= after_creation
    
    def test_token_subject_claim(self):
        """Test token subject claim handling."""
        subjects = [
            "test@example.com",
            "user123",
            "admin@company.com",
            "special-chars_user.name+test@domain.co.uk"
        ]
        
        for subject in subjects:
            data = {"sub": subject}
            token = create_access_token(data)
            payload = verify_token(token)
            
            assert payload["sub"] == subject
    
    @pytest.mark.parametrize("algorithm", ["HS256", "HS384", "HS512"])
    def test_different_jwt_algorithms(self, algorithm):
        """Test JWT creation with different algorithms."""
        with patch.object(settings, 'jwt_algorithm', algorithm):
            data = {"sub": "test@example.com"}
            token = create_access_token(data)
            
            # Verify algorithm in header
            header = jwt.get_unverified_header(token)
            assert header["alg"] == algorithm
            
            # Verify token can be decoded
            payload = verify_token(token)
            assert payload["sub"] == "test@example.com"