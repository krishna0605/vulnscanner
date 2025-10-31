"""
Database models for dashboard functionality.
Follows the project rules schema design for Supabase integration.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from db.session import Base


class ScanStatus(str, Enum):
    """Scan status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Project(Base):
    """
    Projects table for organizing vulnerability scans.
    """
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        sa.ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False
    )
    target_domain: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    scope_rules: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list,
        server_default=sa.text("'[]'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        nullable=False,
        server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    )

    # Relationships
    scan_sessions: Mapped[List["ScanSession"]] = relationship(
        "ScanSession", 
        back_populates="project",
        cascade="all, delete-orphan"
    )


class ScanSession(Base):
    """
    Scan sessions table for tracking vulnerability scan executions.
    """
    __tablename__ = "scan_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[ScanStatus] = mapped_column(
        sa.Enum(ScanStatus),
        nullable=False,
        default=ScanStatus.PENDING
    )
    start_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now()
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True
    )
    configuration: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )
    stats: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'::jsonb")
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("auth.users.id"),
        nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="scan_sessions")
    discovered_urls: Mapped[List["DiscoveredUrl"]] = relationship(
        "DiscoveredUrl",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class DiscoveredUrl(Base):
    """
    Discovered URLs table for storing crawled endpoints.
    """
    __tablename__ = "discovered_urls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("scan_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    url: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    parent_url: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    method: Mapped[str] = mapped_column(sa.String(10), nullable=False, default="GET")
    status_code: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    content_length: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    response_time: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)  # milliseconds
    page_title: Mapped[Optional[str]] = mapped_column(sa.String(500), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now()
    )

    # Relationships
    session: Mapped["ScanSession"] = relationship("ScanSession", back_populates="discovered_urls")
    extracted_forms: Mapped[List["ExtractedForm"]] = relationship(
        "ExtractedForm",
        back_populates="url",
        cascade="all, delete-orphan"
    )
    technology_fingerprints: Mapped[List["TechnologyFingerprint"]] = relationship(
        "TechnologyFingerprint",
        back_populates="url",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        sa.UniqueConstraint("session_id", "url", "method", name="uq_session_url_method"),
    )


class ExtractedForm(Base):
    """
    Extracted forms table for storing discovered forms and their fields.
    """
    __tablename__ = "extracted_forms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )
    url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("discovered_urls.id", ondelete="CASCADE"),
        nullable=False
    )
    form_action: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    form_method: Mapped[Optional[str]] = mapped_column(sa.String(10), nullable=True)
    form_fields: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    csrf_tokens: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=sa.text("'[]'::jsonb")
    )
    authentication_required: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False
    )

    # Relationships
    url: Mapped["DiscoveredUrl"] = relationship("DiscoveredUrl", back_populates="extracted_forms")


class TechnologyFingerprint(Base):
    """
    Technology fingerprints table for storing detected technologies.
    """
    __tablename__ = "technology_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )
    url_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("discovered_urls.id", ondelete="CASCADE"),
        nullable=False
    )
    server_software: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    programming_language: Mapped[Optional[str]] = mapped_column(sa.String(50), nullable=True)
    framework: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    cms: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    javascript_libraries: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=sa.text("'[]'::jsonb")
    )
    security_headers: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'::jsonb")
    )
    detected_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now()
    )

    # Relationships
    url: Mapped["DiscoveredUrl"] = relationship("DiscoveredUrl", back_populates="technology_fingerprints")


class DashboardMetric(Base):
    """
    Dashboard metrics table for storing real-time dashboard data.
    """
    __tablename__ = "dashboard_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )
    metric_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(sa.Float, nullable=False)
    metric_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)  # counter, gauge, histogram
    labels: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'::jsonb")
    )
    timestamp: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now()
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("scan_sessions.id", ondelete="CASCADE"),
        nullable=True
    )

    __table_args__ = (
        sa.Index("idx_dashboard_metrics_name_timestamp", "metric_name", "timestamp"),
        sa.Index("idx_dashboard_metrics_session", "session_id"),
    )


class RealtimeUpdate(Base):
    """
    Real-time updates table for storing WebSocket broadcast data.
    """
    __tablename__ = "realtime_updates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()")
    )
    event_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'::jsonb")
    )
    timestamp: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now()
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("scan_sessions.id", ondelete="CASCADE"),
        nullable=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )

    __table_args__ = (
        sa.Index("idx_realtime_updates_event_type", "event_type"),
        sa.Index("idx_realtime_updates_timestamp", "timestamp"),
        sa.Index("idx_realtime_updates_user", "user_id"),
        sa.Index("idx_realtime_updates_session", "session_id"),
    )