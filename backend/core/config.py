from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  app_name: str = "VulnScanner API"
  secret_key: str = "change-me"
  jwt_algorithm: str = "HS256"
  jwt_exp_minutes: int = 60
  
  # Development mode - allows bypassing authentication
  development_mode: bool = True
  
  # Skip Supabase initialization for local development
  skip_supabase: bool = False

  # Database (Supabase preferred). Provide one of these.
  supabase_db_url: str = ""
  database_url: str = ""

  # Supabase client configuration
  supabase_url: str = ""
  supabase_anon_key: str = ""
  supabase_service_role_key: str = ""

  # CORS
  cors_origins: Union[List[str], str] = ["http://localhost:3000"]

  # Stripe
  stripe_secret_key: str = ""

  # Redis/Celery
  redis_url: str = "redis://localhost:6379/0"

  # CSRF
  csrf_header_name: str = "x-csrf-token"
  csrf_secret: str = ""  # if empty, csrf check disabled (dev)

  @field_validator('cors_origins', mode='before')
  @classmethod
  def parse_cors_origins(cls, v):
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

  model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=False)


settings = Settings()