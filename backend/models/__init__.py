"""
Centralized model imports using the unified models.
The unified models work with both SQLite (development) and PostgreSQL (production).
"""

# Import unified models that work with both SQLite and PostgreSQL
from .unified_models import (
    Profile,
    Project,
    ScanSession,
    DiscoveredUrl,
    ExtractedForm,
    TechnologyFingerprint,
    VulnerabilityType,
    Vulnerability,
    DashboardMetric,
    RealtimeUpdate,
    # Enums
    UserRole,
    ScanStatus,
    ScanType,
    SeverityLevel,
    VulnerabilityCategory,
    VulnerabilityStatus
)

# For backward compatibility, alias Profile as User
User = Profile

# Export all models
__all__ = [
    # Models
    'User',  # Alias for Profile
    'Profile',
    'Project', 
    'ScanSession',
    'DiscoveredUrl',
    'ExtractedForm',
    'TechnologyFingerprint',
    'VulnerabilityType',
    'Vulnerability',
    'DashboardMetric',
    'RealtimeUpdate',
    # Enums
    'UserRole',
    'ScanStatus',
    'ScanType',
    'SeverityLevel',
    'VulnerabilityCategory',
    'VulnerabilityStatus'
]