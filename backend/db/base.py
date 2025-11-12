"""Metadata aggregator for Alembic autogenerate.
Imports all SQLAlchemy models so Base.metadata is populated.
"""
from db.session import Base

# Import models to register with Base.metadata
from models.unified_models import (
    Profile, Project, ScanSession, DiscoveredUrl, ExtractedForm,
    TechnologyFingerprint, VulnerabilityType, Vulnerability, DashboardMetric,
    RealtimeUpdate
)

# Expose metadata for Alembic
metadata = Base.metadata