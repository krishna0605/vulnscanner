"""
Centralized model imports that conditionally load SQLite or PostgreSQL models
based on the SKIP_SUPABASE configuration setting.
"""
from core.config import settings

# Import appropriate models based on configuration
if getattr(settings, 'skip_supabase', False):
    # Use SQLite-compatible models for local development
    from models.sqlite_models import (
        User,
        Project,
        ScanSession,
        DiscoveredUrl,
        ExtractedForm,
        TechnologyFingerprint,
        ScanStatus,
        RealtimeUpdate
    )
else:
    # Use PostgreSQL models for production with Supabase
    from models.user import User
    from models.dashboard import (
        Project,
        ScanSession,
        DiscoveredUrl,
        ExtractedForm,
        TechnologyFingerprint,
        ScanStatus,
        RealtimeUpdate
    )

# Export all models
__all__ = [
    'User',
    'Project', 
    'ScanSession',
    'DiscoveredUrl',
    'ExtractedForm',
    'TechnologyFingerprint',
    'ScanStatus',
    'RealtimeUpdate'
]