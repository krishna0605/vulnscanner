"""
SQLite-compatible models for development.
These models use simpler types that work with SQLite.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


class ScanStatus(str, Enum):
    """Scan status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(Base):
    """Users table for SQLite development."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(255))
    full_name: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())


class Project(Base):
    """Projects table for SQLite development."""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(
        sa.Integer, 
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    target_domain: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    scope_rules: Mapped[list] = mapped_column(
        sa.JSON, 
        nullable=False, 
        default=list
    )
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
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    scan_sessions: Mapped[list["ScanSession"]] = relationship("ScanSession", back_populates="project")


class ScanSession(Base):
    """Scan sessions table for SQLite development."""
    __tablename__ = "scan_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        sa.String(20), 
        nullable=False, 
        default=ScanStatus.PENDING.value
    )
    start_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), 
        nullable=True
    )
    configuration: Mapped[str] = mapped_column(sa.Text, nullable=False)
    stats: Mapped[str] = mapped_column(sa.Text, nullable=False, default="{}")
    created_by: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("users.id"),
        nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="scan_sessions")
    creator: Mapped["User"] = relationship("User")
    discovered_urls: Mapped[list["DiscoveredUrl"]] = relationship("DiscoveredUrl", back_populates="session")


class DiscoveredUrl(Base):
    """Discovered URLs table for SQLite development."""
    __tablename__ = "discovered_urls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("scan_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    url: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    parent_url: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    method: Mapped[str] = mapped_column(sa.String(10), nullable=False, default="GET")
    status_code: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    content_length: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    response_time: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    page_title: Mapped[Optional[str]] = mapped_column(sa.String(500), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )

    # Relationships
    session: Mapped["ScanSession"] = relationship("ScanSession", back_populates="discovered_urls")
    extracted_forms: Mapped[list["ExtractedForm"]] = relationship("ExtractedForm", back_populates="url")
    technology_fingerprints: Mapped[list["TechnologyFingerprint"]] = relationship("TechnologyFingerprint", back_populates="url")


class ExtractedForm(Base):
    """Extracted forms table for SQLite development."""
    __tablename__ = "extracted_forms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("discovered_urls.id", ondelete="CASCADE"),
        nullable=False
    )
    form_action: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    form_method: Mapped[Optional[str]] = mapped_column(sa.String(10), nullable=True)
    form_fields: Mapped[str] = mapped_column(sa.Text, nullable=False)
    csrf_tokens: Mapped[str] = mapped_column(sa.Text, nullable=False, default="[]")
    authentication_required: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)

    # Relationships
    url: Mapped["DiscoveredUrl"] = relationship("DiscoveredUrl", back_populates="extracted_forms")


class TechnologyFingerprint(Base):
    """Technology fingerprints table for SQLite development."""
    __tablename__ = "technology_fingerprints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("discovered_urls.id", ondelete="CASCADE"),
        nullable=False
    )
    server_software: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    programming_language: Mapped[Optional[str]] = mapped_column(sa.String(50), nullable=True)
    framework: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    cms: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    javascript_libraries: Mapped[str] = mapped_column(sa.Text, nullable=False, default="[]")
    security_headers: Mapped[str] = mapped_column(sa.Text, nullable=False, default="{}")
    detected_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), 
        server_default=sa.func.now()
    )

    # Relationships
    url: Mapped["DiscoveredUrl"] = relationship("DiscoveredUrl", back_populates="technology_fingerprints")


class RealtimeUpdate(Base):
    """Real-time updates table for SQLite development."""
    __tablename__ = "realtime_updates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    data: Mapped[str] = mapped_column(sa.Text, nullable=False, default="{}")  # JSON as text for SQLite
    timestamp: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now()
    )
    session_id: Mapped[Optional[int]] = mapped_column(
        sa.Integer,
        sa.ForeignKey("scan_sessions.id", ondelete="CASCADE"),
        nullable=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)

    # Relationships
    session: Mapped[Optional["ScanSession"]] = relationship("ScanSession", back_populates="realtime_updates")


# Add back_populates to User and ScanSession
User.projects = relationship("Project", back_populates="owner")
ScanSession.realtime_updates = relationship("RealtimeUpdate", back_populates="session")