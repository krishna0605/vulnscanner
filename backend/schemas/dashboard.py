"""
Pydantic schemas for dashboard API endpoints.
Defines request/response models for dashboard functionality.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from uuid import UUID
import re
from urllib.parse import urlparse
import ipaddress
from pydantic import BaseModel, Field, ConfigDict, field_validator

from ..models import ScanStatus


# Base schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=3, max_length=100, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    target_domain: str = Field(..., min_length=1, max_length=255, description="Target domain to scan")
    scope_rules: List[str] = Field(default_factory=list, description="URL scope rules (regex patterns)")
    
    @field_validator('target_domain')
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate and normalize target_domain.

        Accepts full URLs like "https://example.com/path" and normalizes to the host
        (e.g., "example.com"). Also accepts raw domains (with or without port) and IPs.
        """
        if not v or not v.strip():
            raise ValueError("Domain cannot be empty")

        raw = v.strip()

        # If it's a URL, extract hostname/netloc
        host = raw
        if '://' in raw:
            parsed = urlparse(raw)
            host = parsed.netloc or parsed.path
        else:
            # Strip any path if present
            host = raw.split('/')[0]

        # Remove credentials
        if '@' in host:
            host = host.split('@')[-1]
        # Remove port
        if ':' in host:
            host = host.split(':')[0]

        host = host.strip().lower()
        if not host:
            raise ValueError("Domain cannot be empty after normalization")

        # Allow localhost
        if host == 'localhost':
            return host

        # Allow IP addresses (IPv4/IPv6)
        try:
            ipaddress.ip_address(host)
            return host
        except ValueError:
            pass

        # Basic domain format validation: letters, numbers, dots, hyphens
        domain_pattern = r'^[a-z0-9]([a-z0-9\-\.]*[a-z0-9])?$'
        if not re.match(domain_pattern, host):
            raise ValueError("Invalid domain format - only letters, numbers, dots, and hyphens allowed")

        # Must contain at least one dot (e.g., example.com)
        if '.' not in host:
            raise ValueError("Domain must contain at least one dot (e.g., example.com)")

        return host


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    target_domain: Optional[str] = Field(None, min_length=1, max_length=255)
    scope_rules: Optional[List[str]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime


# Scan session schemas
class ScanConfigurationSchema(BaseModel):
    """Schema for scan configuration."""
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum crawl depth")
    max_pages: int = Field(default=1000, ge=10, le=100000, description="Maximum pages to crawl")
    requests_per_second: int = Field(default=10, ge=1, le=100, description="Request rate limit")
    max_concurrent_requests: int = Field(default=10, ge=1, le=100, description="Maximum concurrent requests")
    timeout: int = Field(default=30, ge=5, le=300, description="Request timeout in seconds")
    follow_redirects: bool = Field(default=True, description="Follow HTTP redirects")
    respect_robots: bool = Field(default=True, description="Respect robots.txt")
    user_agent: str = Field(default="Enhanced-Vulnerability-Scanner/1.0", description="User agent string")
    scope_patterns: List[str] = Field(default_factory=list, description="URL scope patterns")
    exclude_patterns: List[str] = Field(default_factory=list, description="URL exclude patterns")
    authentication: Optional[Dict[str, Any]] = Field(None, description="Authentication configuration")
    target_url: Optional[str] = Field(None, description="Explicit target URL (overrides project target_domain)")


class ScanSessionCreate(BaseModel):
    """Schema for creating a new scan session."""
    configuration: ScanConfigurationSchema


class ScanSessionUpdate(BaseModel):
    """Schema for updating a scan session."""
    status: Optional[ScanStatus] = None
    end_time: Optional[datetime] = None
    stats: Optional[Dict[str, Any]] = None


class ScanSessionResponse(BaseModel):
    """Schema for scan session response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    status: ScanStatus
    start_time: datetime
    end_time: Optional[datetime]
    configuration: Dict[str, Any]
    stats: Dict[str, Any]
    created_by: UUID
    created_at: Optional[datetime] = None


# URL discovery schemas
class DiscoveredUrlResponse(BaseModel):
    """Schema for discovered URL response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    session_id: UUID
    url: str
    parent_url: Optional[str]
    method: str
    status_code: Optional[int]
    content_type: Optional[str]
    content_length: Optional[int]
    response_time: Optional[int]
    page_title: Optional[str]
    discovered_at: datetime


# Form extraction schemas
class ExtractedFormResponse(BaseModel):
    """Schema for extracted form response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    url_id: UUID
    form_action: Optional[str]
    form_method: Optional[str]
    form_fields: Dict[str, Any]
    csrf_tokens: List[str]
    authentication_required: bool


# Technology fingerprint schemas
class TechnologyFingerprintResponse(BaseModel):
    """Schema for technology fingerprint response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    url_id: UUID
    server_software: Optional[str]
    programming_language: Optional[str]
    framework: Optional[str]
    cms: Optional[str]
    javascript_libraries: List[str]
    security_headers: Dict[str, Any]
    detected_at: datetime


# Dashboard metrics schemas
class DashboardMetricCreate(BaseModel):
    """Schema for creating dashboard metrics."""
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    metric_type: str = Field(..., pattern="^(counter|gauge|histogram)$")
    labels: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[UUID] = None


class DashboardMetricResponse(BaseModel):
    """Schema for dashboard metric response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    metric_name: str
    metric_value: float
    metric_type: str
    labels: Dict[str, Any]
    timestamp: datetime
    session_id: Optional[UUID]


# Dashboard summary schemas
class ProjectSummary(BaseModel):
    """Summary statistics for a project."""
    total_scans: int
    active_scans: int
    completed_scans: int
    failed_scans: int
    total_urls_discovered: int
    total_forms_found: int
    last_scan_date: Optional[datetime]


class ScanSummary(BaseModel):
    """Summary statistics for a scan session."""
    urls_discovered: int
    forms_extracted: int
    technologies_detected: int
    avg_response_time: Optional[float]
    status_code_distribution: Dict[str, int]
    content_type_distribution: Dict[str, int]


class MetricSummary(BaseModel):
    """Summary of key dashboard metrics."""
    scan_completion_rate: float = Field(..., ge=0, le=100, description="Percentage of completed scans")
    avg_scan_duration: float = Field(..., ge=0, description="Average scan duration in minutes")
    urls_per_scan: float = Field(..., ge=0, description="Average URLs discovered per scan")
    forms_per_scan: float = Field(..., ge=0, description="Average forms found per scan")


class DashboardOverview(BaseModel):
    """Overall dashboard overview."""
    total_projects: int
    total_scans: int
    active_scans: int
    total_urls_discovered: int
    total_forms_found: int
    total_technologies_detected: int
    recent_activity: List[Dict[str, Any]]


# Real-time update schemas
class RealTimeUpdate(BaseModel):
    """Schema for real-time updates."""
    event_type: str = Field(..., description="Type of update event")
    data: Dict[str, Any] = Field(..., description="Update data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[UUID] = None


# WebSocket real-time update schemas
class ScanProgressUpdate(BaseModel):
    """Schema for scan progress updates via WebSocket."""
    scan_id: UUID
    status: ScanStatus
    progress_percentage: float = Field(..., ge=0, le=100)
    urls_discovered: int = Field(..., ge=0)
    current_url: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DashboardMetricUpdate(BaseModel):
    """Schema for dashboard metric updates via WebSocket."""
    metric_name: str
    metric_value: float
    metric_type: str
    labels: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Pagination schemas
class PaginationParams(BaseModel):
    """Pagination parameters."""
    limit: int = Field(default=50, ge=1, le=1000, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


# Filter schemas
class ScanSessionFilter(BaseModel):
    """Filter parameters for scan sessions."""
    status: Optional[ScanStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_id: Optional[UUID] = None


class UrlDiscoveryFilter(BaseModel):
    """Filter parameters for discovered URLs."""
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    method: Optional[str] = None
    has_forms: Optional[bool] = None