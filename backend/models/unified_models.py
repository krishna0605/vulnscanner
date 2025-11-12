"""
Unified database models for VulnScanner.
Works with both SQLite (development) and PostgreSQL (production/Supabase).
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid
import json

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import DateTime

from backend.db.session import Base
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


# =====================================================
# ENUMERATIONS
# =====================================================

class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class ScanStatus(str, Enum):
    """Scan status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanType(str, Enum):
    """Scan type enumeration."""
    DISCOVERY = "discovery"
    VULNERABILITY = "vulnerability"
    FULL = "full"
    CUSTOM = "custom"


class SeverityLevel(str, Enum):
    """Severity level enumeration."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VulnerabilityCategory(str, Enum):
    """Vulnerability category enumeration."""
    INJECTION = "injection"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    EXPOSURE = "exposure"
    CONFIGURATION = "configuration"
    CRYPTOGRAPHY = "cryptography"
    BUSINESS_LOGIC = "business_logic"
    OTHER = "other"


class VulnerabilityStatus(str, Enum):
    """Vulnerability status enumeration."""
    OPEN = "open"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    FIXED = "fixed"
    ACCEPTED_RISK = "accepted_risk"
    DUPLICATE = "duplicate"


# =====================================================
# CORE USER AND AUTHENTICATION MODELS
# =====================================================

class Profile(Base):
    """
    User profiles table (extends Supabase auth.users).
    For SQLite development, this acts as the main users table.
    """
    __tablename__ = "profiles"
    __tablename__ = "projects"
    __tablename__ = "projects"
    __tablename__ = "projects"

    # Use UUID for PostgreSQL, Integer for SQLite
    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    username: Mapped[Optional[str]] = mapped_column(sa.String(50), unique=True, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    role: Mapped[str] = mapped_column(sa.String(20), default=UserRole.USER.value)
    organization: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(sa.String(50), default="UTC")
    
    # JSON fields - use Text for SQLite, JSONB for PostgreSQL
    _preferences: Mapped[str] = mapped_column("preferences", sa.Text, default="{}")
    
    @hybrid_property
    def preferences(self) -> Dict[str, Any]:
        """Get preferences as a Python dict"""
        try:
            return json.loads(self._preferences) if self._preferences else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @preferences.setter
    def preferences(self, value: Dict[str, Any]):
        """Set preferences from a Python dict"""
        self._preferences = json.dumps(value) if value is not None else "{}"
    
    # SQLite-specific fields for development
    hashed_password: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    email_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    
    last_login_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    )

    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project", 
        back_populates="owner",
        cascade="all, delete-orphan"
    )


# =====================================================
# PROJECT MANAGEMENT MODELS
# =====================================================

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"))
    target_domain = Column(String(255), nullable=False)
    scope_rules = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # JSON fields
    _scope_rules: Mapped[str] = mapped_column("scope_rules", sa.Text, default="[]")

    @hybrid_property
    def scope_rules(self) -> List[str]:
        """Get scope_rules as a Python list"""
        try:
            return json.loads(self._scope_rules) if self._scope_rules else []
        except (json.JSONDecodeError, TypeError):
            return []

    @scope_rules.setter
    def scope_rules(self, value: List[str]):
        """Set scope_rules from a Python list"""
        self._scope_rules = json.dumps(value) if value is not None else "[]"

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    )

    # Relationships
    owner: Mapped["Profile"] = relationship("Profile", back_populates="projects")
    scan_sessions: Mapped[List["ScanSession"]] = relationship(
        "ScanSession", 
        back_populates="project",
        cascade="all, delete-orphan"
    )


# =====================================================
# SCAN EXECUTION MODELS
# =====================================================

class ScanSession(Base):
    """
    Scan sessions table for tracking vulnerability scan executions.
    """
    __tablename__ = "scan_sessions"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(sa.String(20), default=ScanStatus.PENDING.value)
    scan_type: Mapped[str] = mapped_column(sa.String(20), default=ScanType.DISCOVERY.value)
    start_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    )
    
    # JSON fields
    _configuration: Mapped[str] = mapped_column("configuration", sa.Text, default="{}")
    _stats: Mapped[str] = mapped_column("stats", sa.Text, default="{}")
    
    @hybrid_property
    def configuration(self) -> Dict[str, Any]:
        """Get configuration as a Python dict"""
        try:
            return json.loads(self._configuration) if self._configuration else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @configuration.setter
    def configuration(self, value: Dict[str, Any]):
        """Set configuration from a Python dict"""
        self._configuration = json.dumps(value) if value is not None else "{}"
    
    @hybrid_property
    def stats(self) -> Dict[str, Any]:
        """Get stats as a Python dict"""
        try:
            return json.loads(self._stats) if self._stats else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @stats.setter
    def stats(self, value: Dict[str, Any]):
        """Set stats from a Python dict"""
        self._stats = json.dumps(value) if value is not None else "{}"
    
    created_by: Mapped[Optional[str]] = mapped_column(
        sa.String(36),
        sa.ForeignKey("profiles.id"),
        nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="scan_sessions")
    discovered_urls: Mapped[List["DiscoveredUrl"]] = relationship(
        "DiscoveredUrl", 
        back_populates="session",
        cascade="all, delete-orphan"
    )
    vulnerabilities: Mapped[List["Vulnerability"]] = relationship(
        "Vulnerability", 
        back_populates="session",
        cascade="all, delete-orphan"
    )


class DiscoveredUrl(Base):
    """
    Discovered URLs table for storing crawled URLs and their metadata.
    """
    __tablename__ = "discovered_urls"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("scan_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    url: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    parent_url: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    method: Mapped[str] = mapped_column(sa.String(10), default="GET")
    status_code: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    content_length: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    response_time: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)  # milliseconds
    page_title: Mapped[Optional[str]] = mapped_column(sa.String(500), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )

    # Relationships
    session: Mapped["ScanSession"] = relationship("ScanSession", back_populates="discovered_urls")
    forms: Mapped[List["ExtractedForm"]] = relationship(
        "ExtractedForm", 
        back_populates="url",
        cascade="all, delete-orphan"
    )
    technology_fingerprints: Mapped[List["TechnologyFingerprint"]] = relationship(
        "TechnologyFingerprint", 
        back_populates="url",
        cascade="all, delete-orphan"
    )

    # Unique constraint
    __table_args__ = (
        sa.UniqueConstraint('session_id', 'url', 'method', name='uq_session_url_method'),
    )


class ExtractedForm(Base):
    """
    Extracted forms table for storing HTML forms found during crawling.
    """
    __tablename__ = "extracted_forms"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    url_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("discovered_urls.id", ondelete="CASCADE"),
        nullable=False
    )
    form_action: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    form_method: Mapped[str] = mapped_column(sa.String(10), default="GET")
    
    # JSON fields
    _form_fields: Mapped[str] = mapped_column("form_fields", sa.Text, default="[]")
    _csrf_tokens: Mapped[str] = mapped_column("csrf_tokens", sa.Text, default="[]")
    
    @hybrid_property
    def form_fields(self) -> List[Dict[str, Any]]:
        """Get form_fields as a Python list"""
        try:
            return json.loads(self._form_fields) if self._form_fields else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @form_fields.setter
    def form_fields(self, value: List[Dict[str, Any]]):
        """Set form_fields from a Python list"""
        self._form_fields = json.dumps(value) if value is not None else "[]"
    
    @hybrid_property
    def csrf_tokens(self) -> List[str]:
        """Get csrf_tokens as a Python list"""
        try:
            return json.loads(self._csrf_tokens) if self._csrf_tokens else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @csrf_tokens.setter
    def csrf_tokens(self, value: List[str]):
        """Set csrf_tokens from a Python list"""
        self._csrf_tokens = json.dumps(value) if value is not None else "[]"
    
    authentication_required: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    # Relationships
    url: Mapped["DiscoveredUrl"] = relationship("DiscoveredUrl", back_populates="forms")


class TechnologyFingerprint(Base):
    """
    Technology fingerprints table for storing detected technologies.
    """
    __tablename__ = "technology_fingerprints"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    url_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("discovered_urls.id", ondelete="CASCADE"),
        nullable=False
    )
    server_software: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    programming_language: Mapped[Optional[str]] = mapped_column(sa.String(50), nullable=True)
    framework: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    cms: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    
    # JSON fields
    _javascript_libraries: Mapped[str] = mapped_column("javascript_libraries", sa.Text, default="[]")
    _security_headers: Mapped[str] = mapped_column("security_headers", sa.Text, default="{}")
    
    @hybrid_property
    def javascript_libraries(self) -> List[str]:
        """Get javascript_libraries as a Python list"""
        try:
            return json.loads(self._javascript_libraries) if self._javascript_libraries else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @javascript_libraries.setter
    def javascript_libraries(self, value: List[str]):
        """Set javascript_libraries from a Python list"""
        self._javascript_libraries = json.dumps(value) if value is not None else "[]"
    
    @hybrid_property
    def security_headers(self) -> Dict[str, str]:
        """Get security_headers as a Python dict"""
        try:
            return json.loads(self._security_headers) if self._security_headers else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @security_headers.setter
    def security_headers(self, value: Dict[str, str]):
        """Set security_headers from a Python dict"""
        self._security_headers = json.dumps(value) if value is not None else "{}"
    
    detected_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )

    # Relationships
    url: Mapped["DiscoveredUrl"] = relationship("DiscoveredUrl", back_populates="technology_fingerprints")


# =====================================================
# VULNERABILITY MODELS
# =====================================================

class VulnerabilityType(Base):
    """
    Vulnerability types and definitions.
    """
    __tablename__ = "vulnerability_types"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    severity: Mapped[str] = mapped_column(sa.String(20), default=SeverityLevel.MEDIUM.value)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    impact: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    remediation: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    
    # JSON fields
    _references: Mapped[str] = mapped_column("references", sa.Text, default="[]")
    
    @hybrid_property
    def references(self) -> List[str]:
        """Get references as a Python list"""
        try:
            return json.loads(self._references) if self._references else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @references.setter
    def references(self, value: List[str]):
        """Set references from a Python list"""
        self._references = json.dumps(value) if value is not None else "[]"
    
    cwe_id: Mapped[Optional[str]] = mapped_column(sa.String(20), nullable=True)
    owasp_category: Mapped[Optional[str]] = mapped_column(sa.String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    )

    # Relationships
    vulnerabilities: Mapped[List["Vulnerability"]] = relationship(
        "Vulnerability", 
        back_populates="vulnerability_type"
    )


class Vulnerability(Base):
    """
    Identified vulnerabilities and security issues.
    """
    __tablename__ = "vulnerabilities"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("scan_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    url_id: Mapped[Optional[str]] = mapped_column(
        sa.String(36),
        sa.ForeignKey("discovered_urls.id", ondelete="SET NULL"),
        nullable=True
    )
    vulnerability_type_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("vulnerability_types.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    severity: Mapped[str] = mapped_column(sa.String(20), default=SeverityLevel.MEDIUM.value)
    confidence: Mapped[float] = mapped_column(sa.Float, default=0.0)
    impact_score: Mapped[int] = mapped_column(sa.Integer, default=0)
    exploitability_score: Mapped[int] = mapped_column(sa.Integer, default=0)
    
    # JSON fields
    _evidence: Mapped[str] = mapped_column("evidence", sa.Text, default="{}")
    
    @hybrid_property
    def evidence(self) -> Dict[str, Any]:
        """Get evidence as a Python dict"""
        try:
            return json.loads(self._evidence) if self._evidence else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @evidence.setter
    def evidence(self, value: Dict[str, Any]):
        """Set evidence from a Python dict"""
        self._evidence = json.dumps(value) if value is not None else "{}"
    
    proof_of_concept: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    remediation_steps: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    false_positive: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    status: Mapped[str] = mapped_column(sa.String(20), default=VulnerabilityStatus.OPEN.value)
    assigned_to: Mapped[Optional[str]] = mapped_column(
        sa.String(36),
        sa.ForeignKey("profiles.id"),
        nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    )

    # Relationships
    session: Mapped["ScanSession"] = relationship("ScanSession", back_populates="vulnerabilities")
    vulnerability_type: Mapped["VulnerabilityType"] = relationship("VulnerabilityType", back_populates="vulnerabilities")


# =====================================================
# DASHBOARD AND METRICS MODELS
# =====================================================

class DashboardMetric(Base):
    """
    Dashboard metrics for real-time updates and analytics.
    """
    __tablename__ = "dashboard_metrics"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    metric_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    metric_value: Mapped[float] = mapped_column(sa.Float, nullable=False)
    
    # JSON fields
    _metric_metadata: Mapped[str] = mapped_column("metric_metadata", sa.Text, default="{}")
    
    @hybrid_property
    def metric_metadata(self) -> Dict[str, Any]:
        """Get metric metadata as a Python dict"""
        try:
            return json.loads(self._metric_metadata) if self._metric_metadata else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @metric_metadata.setter
    def metric_metadata(self, value: Dict[str, Any]):
        """Set metric metadata from a Python dict"""
        self._metric_metadata = json.dumps(value) if value is not None else "{}"
    
    recorded_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )

    # Index for efficient queries
    __table_args__ = (
        sa.Index('idx_dashboard_metrics_user_type_time', 'user_id', 'metric_type', 'recorded_at'),
    )


class RealtimeUpdate(Base):
    """
    Real-time updates for WebSocket notifications.
    """
    __tablename__ = "realtime_updates"

    id: Mapped[str] = mapped_column(
        sa.String(36),  # UUID as string for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    
    # JSON fields
    _event_data: Mapped[str] = mapped_column("event_data", sa.Text, default="{}")
    
    @hybrid_property
    def event_data(self) -> Dict[str, Any]:
        """Get event_data as a Python dict"""
        try:
            return json.loads(self._event_data) if self._event_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @event_data.setter
    def event_data(self, value: Dict[str, Any]):
        """Set event_data from a Python dict"""
        self._event_data = json.dumps(value) if value is not None else "{}"
    
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    processed: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    # Index for efficient queries
    __table_args__ = (
        sa.Index('idx_realtime_updates_user_processed', 'user_id', 'processed', 'created_at'),
    )