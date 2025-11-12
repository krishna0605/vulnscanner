from typing import List, Union, Literal
from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import logging

# Set up logging for configuration validation
logger = logging.getLogger(__name__)

# Default insecure keys that must be changed in production
INSECURE_DEFAULT_KEYS = {
    "change-me",
    "your-secret-key-here", 
    "your-super-secret-jwt-key-change-this-in-production",
    "your-csrf-secret-key",
    "jUca4mpVxi1q_lUGpTmhGUXiRaVVquGaO8sjPRHyhy8",  # Example from generator
}


class Settings(BaseSettings):
    # =============================================================================
    # APPLICATION IDENTIFICATION
    # =============================================================================
    app_name: str = "VulnScanner API"
    
    # =============================================================================
    # ENVIRONMENT CONFIGURATION
    # =============================================================================
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    secret_key: str = "change-me"
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    session_secret: str = ""
    api_key: str = ""
    
    # Development mode - allows bypassing authentication
    development_mode: bool = True
    
    # Deprecated flags related to external auth providers have been removed

    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    # Database connection URLs (local Postgres or SQLite)
    database_url: str = ""
    # Explicit async/sync URLs for PostgreSQL connectivity
    database_url_async: str = ""
    database_url_sync: str = ""
    # Use host.docker.internal when running API in Docker talking to host DB
    use_host_docker_internal: bool = False
    db_echo: bool = False

    # External provider configuration removed (Supabase no longer used)

    # =============================================================================
    # CORS CONFIGURATION
    # =============================================================================
    cors_origins: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:3010",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3010"
    ]

    # =============================================================================
    # CSRF PROTECTION
    # =============================================================================
    csrf_header_name: str = "x-csrf-token"
    csrf_secret: str = ""  # if empty, csrf check disabled (dev)

    # =============================================================================
    # REDIS/CELERY CONFIGURATION
    # =============================================================================
    # Redis cache (general purpose)
    redis_url: str = "redis://localhost:6379/0"
    # Celery broker/result configuration
    # Defaults for local development (no Docker): RabbitMQ broker, Redis DB 1 backend
    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "redis://localhost:6379/1"
    # Default task queue for crawler tasks
    celery_queue: str = "crawler"

    # =============================================================================
    # CRAWLER CONFIGURATION
    # =============================================================================
    crawler_max_depth: int = 3
    crawler_max_pages: int = 1000
    crawler_requests_per_second: int = 10
    crawler_timeout: int = 30
    crawler_user_agent: str = "VulnScanner/1.0"

    # =============================================================================
    # SECURITY HEADERS
    # =============================================================================
    security_headers_enabled: bool = True
    hsts_max_age: int = 31536000
    csp_enabled: bool = True

    # =============================================================================
    # VALIDATORS
    # =============================================================================
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret key is not using insecure defaults."""
        if v in INSECURE_DEFAULT_KEYS:
            if os.getenv('APP_ENV') == 'production':
                raise ValueError(
                    "Default secret key detected in production! "
                    "Generate secure keys using: python generate_secure_keys.py"
                )
            else:
                logger.warning(
                    "Using default secret key in development. "
                    "Generate secure keys for production using: python generate_secure_keys.py"
                )
        
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        
        return v

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        """Validate JWT secret key."""
        if not v:
            logger.warning("JWT secret key not set, using main secret key")
            return ""
        
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        
        return v

    @field_validator('app_env')
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Validate application environment."""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"APP_ENV must be one of: {valid_envs}")
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v_upper

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            if v.startswith('[') and v.endswith(']'):
                # Handle JSON array string
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    # Fallback to comma-separated
                    return [origin.strip() for origin in v.strip('[]').split(',') if origin.strip()]
            else:
                # Handle comma-separated string
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # Removed Supabase-specific validators

    @field_validator('crawler_max_depth')
    @classmethod
    def validate_crawler_max_depth(cls, v: int) -> int:
        """Validate crawler max depth."""
        if v < 1 or v > 10:
            raise ValueError("CRAWLER_MAX_DEPTH must be between 1 and 10")
        return v

    @field_validator('crawler_max_pages')
    @classmethod
    def validate_crawler_max_pages(cls, v: int) -> int:
        """Validate crawler max pages."""
        if v < 10 or v > 100000:
            raise ValueError("CRAWLER_MAX_PAGES must be between 10 and 100,000")
        return v

    @field_validator('crawler_requests_per_second')
    @classmethod
    def validate_crawler_rps(cls, v: int) -> int:
        """Validate crawler requests per second."""
        if v < 1 or v > 100:
            raise ValueError("CRAWLER_REQUESTS_PER_SECOND must be between 1 and 100")
        return v

    def validate_production_config(self) -> List[str]:
        """Validate configuration for production deployment."""
        issues = []
        
        if self.app_env == "production":
            # Check for insecure defaults
            if self.secret_key in INSECURE_DEFAULT_KEYS:
                issues.append("SECRET_KEY is using default value")
            
            if self.debug:
                issues.append("DEBUG should be False in production")
            
            if self.development_mode:
                issues.append("DEVELOPMENT_MODE should be False in production")
            
            if not self.database_url and not self.database_url_async and not self.database_url_sync:
                issues.append("Database URL must be configured")
            
            if not self.csrf_secret:
                issues.append("CSRF_SECRET should be set in production")
            
            if self.log_level == "DEBUG":
                issues.append("LOG_LEVEL should not be DEBUG in production")
        
        return issues

    def get_effective_jwt_secret(self) -> str:
        """Get the effective JWT secret key."""
        return self.jwt_secret_key or self.secret_key

    def get_database_url(self) -> str:
        """Get the effective database URL (legacy field for backward compatibility)."""
        return self.database_url or self.database_url_async

    def get_database_url_async(self) -> str:
        """Prefer explicit async URL, then fall back to database_url."""
        return (
            self.database_url_async
            or self.database_url
        )

    def get_database_url_sync(self) -> str:
        """Prefer explicit sync URL for Alembic."""
        return (
            self.database_url_sync
            or self.database_url
        )

    # -----------------------------------------------------------------------------
    # Celery broker/result helpers
    # -----------------------------------------------------------------------------
    def _swap_localhost(self, url: str) -> str:
        """Swap localhost/127.0.0.1 with host.docker.internal when requested.

        Use when the API runs in Docker and broker/result backend are on the host.
        """
        if not url:
            return url
        if not self.use_host_docker_internal:
            return url
        return (
            url.replace("localhost", "host.docker.internal")
               .replace("127.0.0.1", "host.docker.internal")
        )

    def get_broker_url(self) -> str:
        """Return effective Celery broker URL with optional Docker host mapping."""
        env_url = os.getenv("CELERY_BROKER_URL", self.celery_broker_url)
        return self._swap_localhost(env_url)

    def get_result_backend_url(self) -> str:
        """Return effective Celery result backend URL with optional Docker host mapping."""
        env_url = os.getenv("CELERY_RESULT_BACKEND", self.celery_result_backend)
        return self._swap_localhost(env_url)

    def get_runtime_db_url(self) -> str:
        """Return normalized runtime DB URL for async engine.

        - Prefer `database_url_async`; fallback to `database_url` or `supabase_db_url`
        - Normalize to `postgresql+asyncpg` for Postgres
        - Normalize to `sqlite+aiosqlite` for SQLite
        - If `use_host_docker_internal` is True and host is `localhost`,
          substitute host with `host.docker.internal` (for Docker→host connectivity).
        """
        raw = self.get_database_url_async()
        if not raw:
            raw = "sqlite+aiosqlite:///./dev.db"

        # Host substitution for Docker
        if self.use_host_docker_internal and ("localhost:" in raw or "@localhost" in raw):
            raw = raw.replace("@localhost", "@host.docker.internal")
            raw = raw.replace("localhost:", "host.docker.internal:")

        # Normalize drivers for runtime
        if raw.startswith("postgres://"):
            raw = raw.replace("postgres://", "postgresql+asyncpg://", 1)
        elif raw.startswith("postgresql://") and "+asyncpg" not in raw and "+psycopg" not in raw:
            raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)

        if raw.startswith("sqlite://") and "+aiosqlite" not in raw:
            raw = raw.replace("sqlite://", "sqlite+aiosqlite://", 1)

        # Supabase-specific SSL enforcement removed; use environment defaults

        return raw

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],  # Look for .env in current dir and parent dir
        env_prefix="", 
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )


# Initialize settings and validate
try:
    settings = Settings()
    
    # Validate production configuration
    if settings.is_production():
        production_issues = settings.validate_production_config()
        if production_issues:
            error_msg = "Production configuration issues found:\n" + "\n".join(f"- {issue}" for issue in production_issues)
            raise ValidationError(error_msg)
    
    # Log configuration status
    logger.info(f"Configuration loaded successfully for {settings.app_env} environment")
    
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise