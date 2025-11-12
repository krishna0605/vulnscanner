"""Unit tests for core.config module."""

import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError

from core.config import Settings, INSECURE_DEFAULT_KEYS


class TestSettings:
    """Test Settings configuration class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.app_name == "VulnScanner API"
        assert settings.app_env == "development"
        assert settings.debug is True
        assert settings.log_level == "INFO"
        assert settings.development_mode is True
        assert settings.skip_supabase is True

    def test_environment_override(self):
        """Test environment variable override."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'DEBUG': 'false',
            'LOG_LEVEL': 'WARNING',
            'SECRET_KEY': 'production-secret-key-with-sufficient-length',
            'SUPABASE_DB_URL': 'postgresql://user:pass@host:5432/db?sslmode=require'
        }):
            settings = Settings()
            assert settings.app_env == "production"
            assert settings.debug is False
            assert settings.log_level == "WARNING"

    def test_production_environment_validation(self):
        """Test production environment validation."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'SECRET_KEY': 'secure-production-key-with-sufficient-length',
            'DEBUG': 'false',
            'DEVELOPMENT_MODE': 'false',
            'SUPABASE_DB_URL': 'postgresql://user:pass@host:5432/db?sslmode=require'
        }):
            settings = Settings()
            assert settings.is_production() is True
            assert settings.is_development() is False

    def test_development_environment_validation(self):
        """Test development environment validation."""
        settings = Settings()
        assert settings.is_development() is True
        assert settings.is_production() is False

    def test_insecure_secret_key_development(self):
        """Test insecure secret key warning in development."""
        with patch.dict(os.environ, {'SECRET_KEY': 'change-me-but-make-it-long-enough-for-validation'}):
            # Should not raise in development
            settings = Settings()
            assert settings.secret_key == "change-me-but-make-it-long-enough-for-validation"

    @pytest.mark.parametrize("insecure_key", list(INSECURE_DEFAULT_KEYS))
    def test_insecure_secret_key_production(self, insecure_key):
        """Test insecure secret key rejection in production."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'SECRET_KEY': insecure_key
        }):
            with pytest.raises(ValidationError):
                Settings()

    def test_short_secret_key_validation(self):
        """Test secret key length validation."""
        with patch.dict(os.environ, {'SECRET_KEY': 'short'}):
            with pytest.raises(ValidationError):
                Settings()

    def test_jwt_secret_key_fallback(self):
        """Test JWT secret key fallback to main secret."""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'main-secret-key-with-sufficient-length',
            'JWT_SECRET_KEY': ''  # Explicitly empty
        }):
            settings = Settings()
            assert settings.get_effective_jwt_secret() == settings.secret_key

    def test_jwt_secret_key_override(self):
        """Test JWT secret key override."""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'main-secret-key-with-sufficient-length',
            'JWT_SECRET_KEY': 'jwt-specific-secret-key-with-length'
        }):
            settings = Settings()
            assert settings.get_effective_jwt_secret() == settings.jwt_secret_key

    def test_database_url_fallback(self):
        """Test database URL fallback logic."""
        with patch.dict(os.environ, {
            'SUPABASE_DB_URL': 'postgresql://user:pass@host/db',
            'DATABASE_URL': 'sqlite:///fallback.db'
        }):
            settings = Settings()
            assert settings.get_database_url() == settings.supabase_db_url

    def test_database_url_fallback_empty_supabase(self):
        """Test database URL fallback when Supabase URL is empty."""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'sqlite:///fallback.db',
            'SUPABASE_DB_URL': ''  # Explicitly empty
        }):
            settings = Settings()
            assert settings.get_database_url() == 'sqlite:///fallback.db'

    def test_cors_origins_string_parsing(self):
        """Test CORS origins parsing from string."""
        with patch.dict(os.environ, {
            'CORS_ORIGINS': 'http://localhost:3000,https://example.com'
        }):
            settings = Settings()
            assert settings.cors_origins == ['http://localhost:3000', 'https://example.com']

    def test_cors_origins_json_parsing(self):
        """Test CORS origins parsing from JSON string."""
        with patch.dict(os.environ, {
            'CORS_ORIGINS': '["http://localhost:3000", "https://example.com"]'
        }):
            settings = Settings()
            assert settings.cors_origins == ['http://localhost:3000', 'https://example.com']

    def test_supabase_configuration(self):
        """Test Supabase configuration."""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://project.supabase.co',
            'SUPABASE_ANON_KEY': 'anon-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'service-role-key'
        }):
            settings = Settings()
            assert settings.supabase_url == 'https://project.supabase.co'
            assert settings.supabase_anon_key == 'anon-key'
            assert settings.supabase_service_role_key == 'service-role-key'

    def test_redis_celery_configuration(self):
        """Test Redis and Celery configuration."""
        with patch.dict(os.environ, {
            'REDIS_URL': 'redis://localhost:6380/1',
            'CELERY_BROKER_URL': 'redis://localhost:6380/2',
            'CELERY_RESULT_BACKEND': 'redis://localhost:6380/3'
        }):
            settings = Settings()
            assert settings.redis_url == 'redis://localhost:6380/1'
            assert settings.celery_broker_url == 'redis://localhost:6380/2'
            assert settings.celery_result_backend == 'redis://localhost:6380/3'

    def test_crawler_configuration(self):
        """Test crawler configuration."""
        with patch.dict(os.environ, {
            'CRAWLER_MAX_DEPTH': '5',
            'CRAWLER_MAX_PAGES': '2000',
            'CRAWLER_REQUESTS_PER_SECOND': '20',
            'CRAWLER_TIMEOUT': '60',
            'CRAWLER_USER_AGENT': 'CustomScanner/2.0'
        }):
            settings = Settings()
            assert settings.crawler_max_depth == 5
            assert settings.crawler_max_pages == 2000
            assert settings.crawler_requests_per_second == 20
            assert settings.crawler_timeout == 60
            assert settings.crawler_user_agent == 'CustomScanner/2.0'

    def test_security_headers_configuration(self):
        """Test security headers configuration."""
        with patch.dict(os.environ, {
            'SECURITY_HEADERS_ENABLED': 'false',
            'HSTS_MAX_AGE': '86400',
            'CSP_ENABLED': 'false'
        }):
            settings = Settings()
            assert settings.security_headers_enabled is False
            assert settings.hsts_max_age == 86400
            assert settings.csp_enabled is False

    def test_complete_production_config(self):
        """Test complete production configuration."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'SECRET_KEY': 'production-secret-key-with-sufficient-length',
            'JWT_SECRET_KEY': 'production-jwt-secret-key-with-length',
            'DEBUG': 'false',
            'DEVELOPMENT_MODE': 'false',
            'SUPABASE_DB_URL': 'postgresql://user:pass@host/db?sslmode=require',
            'CSRF_SECRET': 'production-csrf-secret-key-with-length',
            'LOG_LEVEL': 'INFO'
        }):
            settings = Settings()
            issues = settings.validate_production_config()
            assert len(issues) == 0

    @pytest.mark.parametrize("insecure_key", list(INSECURE_DEFAULT_KEYS))
    def test_all_insecure_keys_detected(self, insecure_key):
        """Test that all insecure default keys are properly detected."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'SECRET_KEY': insecure_key
        }):
            with pytest.raises(ValidationError):
                Settings()

    def test_invalid_environment_validation(self):
        """Test invalid environment validation."""
        with patch.dict(os.environ, {'APP_ENV': 'invalid'}):
            with pytest.raises(ValidationError):
                Settings()

    def test_invalid_log_level_validation(self):
        """Test invalid log level validation."""
        with patch.dict(os.environ, {'LOG_LEVEL': 'INVALID'}):
            with pytest.raises(ValidationError):
                Settings()

    def test_crawler_validation_bounds(self):
        """Test crawler configuration validation bounds."""
        # Test max_depth bounds
        with patch.dict(os.environ, {'CRAWLER_MAX_DEPTH': '0'}):
            with pytest.raises(ValidationError):
                Settings()
        
        with patch.dict(os.environ, {'CRAWLER_MAX_DEPTH': '11'}):
            with pytest.raises(ValidationError):
                Settings()
        
        # Test max_pages bounds
        with patch.dict(os.environ, {'CRAWLER_MAX_PAGES': '5'}):
            with pytest.raises(ValidationError):
                Settings()
        
        with patch.dict(os.environ, {'CRAWLER_MAX_PAGES': '200000'}):
            with pytest.raises(ValidationError):
                Settings()
        
        # Test requests_per_second bounds
        with patch.dict(os.environ, {'CRAWLER_REQUESTS_PER_SECOND': '0'}):
            with pytest.raises(ValidationError):
                Settings()
        
        with patch.dict(os.environ, {'CRAWLER_REQUESTS_PER_SECOND': '150'}):
            with pytest.raises(ValidationError):
                Settings()

    def test_integer_environment_variables(self):
        """Test integer environment variable parsing."""
        with patch.dict(os.environ, {
            'JWT_EXP_MINUTES': '120',
            'CRAWLER_TIMEOUT': '45'
        }):
            settings = Settings()
            assert settings.jwt_exp_minutes == 120
            assert settings.crawler_timeout == 45

    def test_boolean_environment_variables(self):
        """Test boolean environment variable parsing."""
        with patch.dict(os.environ, {
            'DEBUG': 'true',
            'DEVELOPMENT_MODE': 'false',
            'SKIP_SUPABASE': 'true',
            'DB_ECHO': 'false'
        }):
            settings = Settings()
            assert settings.debug is True
            assert settings.development_mode is False
            assert settings.skip_supabase is True
            assert settings.db_echo is False

    def test_sqlite_database_url_validation(self):
        """Test SQLite database URL validation in development."""
        with patch.dict(os.environ, {
            'APP_ENV': 'development',
            'SUPABASE_DB_URL': 'sqlite:///test.db'
        }):
            settings = Settings()
            assert settings.supabase_db_url == 'sqlite:///test.db'

    def test_postgresql_database_url_validation(self):
        """Test PostgreSQL database URL validation."""
        with patch.dict(os.environ, {
            'SUPABASE_DB_URL': 'postgresql://user:pass@host/db?sslmode=require'
        }):
            settings = Settings()
            assert 'postgresql://' in settings.supabase_db_url

    def test_production_database_validation(self):
        """Test that production requires PostgreSQL."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'SECRET_KEY': 'production-secret-key-with-sufficient-length',
            'SUPABASE_DB_URL': 'sqlite:///test.db'
        }):
            with pytest.raises(ValidationError):
                Settings()

    def test_csrf_configuration(self):
        """Test CSRF configuration."""
        with patch.dict(os.environ, {
            'CSRF_HEADER_NAME': 'x-custom-csrf',
            'CSRF_SECRET': 'csrf-secret-key-with-sufficient-length'
        }):
            settings = Settings()
            assert settings.csrf_header_name == 'x-custom-csrf'
            assert settings.csrf_secret == 'csrf-secret-key-with-sufficient-length'

    def test_api_key_configuration(self):
        """Test API key configuration."""
        with patch.dict(os.environ, {
            'API_KEY': 'test-api-key'
        }):
            settings = Settings()
            assert settings.api_key == 'test-api-key'

    def test_session_secret_configuration(self):
        """Test session secret configuration."""
        with patch.dict(os.environ, {
            'SESSION_SECRET': 'session-secret-key'
        }):
            settings = Settings()
            assert settings.session_secret == 'session-secret-key'