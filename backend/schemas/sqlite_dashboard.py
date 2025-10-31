"""
SQLite-compatible Pydantic schemas for dashboard API endpoints.
These schemas use integer IDs instead of UUIDs to match SQLite models.
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

from models import ScanStatus


# Base schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    target_domain: str = Field(..., min_length=1, max_length=255, description="Target domain to scan")
    scope_rules: List[str] = Field(default_factory=list, description="URL scope rules (regex patterns)")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    target_domain: Optional[str] = Field(None, min_length=1, max_length=255)
    scope_rules: Optional[List[str]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    @field_validator('scope_rules', mode='before')
    @classmethod
    def parse_scope_rules(cls, v):
        """Parse scope_rules from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []


# Scan session schemas
class ScanConfigurationSchema(BaseModel):
    """Schema for scan configuration."""
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum crawl depth")
    max_pages: int = Field(default=1000, ge=10, le=100000, description="Maximum pages to crawl")
    requests_per_second: int = Field(default=10, ge=1, le=100, description="Request rate limit")
    timeout: int = Field(default=30, ge=5, le=300, description="Request timeout in seconds")
    follow_redirects: bool = Field(default=True, description="Follow HTTP redirects")
    respect_robots: bool = Field(default=True, description="Respect robots.txt")
    user_agent: str = Field(default="Enhanced-Vulnerability-Scanner/1.0", description="User agent string")
    scope_patterns: List[str] = Field(default_factory=list, description="URL scope patterns")
    exclude_patterns: List[str] = Field(default_factory=list, description="URL exclude patterns")
    authentication: Optional[Dict[str, Any]] = Field(None, description="Authentication configuration")


class ScanSessionCreate(BaseModel):
    """Schema for creating a new scan session."""
    configuration: ScanConfigurationSchema


class ScanSessionResponse(BaseModel):
    """Schema for scan session response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    status: ScanStatus
    start_time: datetime
    end_time: Optional[datetime]
    configuration: Dict[str, Any]
    stats: Dict[str, Any]
    created_by: int
    
    @field_validator('configuration', mode='before')
    @classmethod
    def parse_configuration(cls, v):
        """Parse configuration from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v if v is not None else {}
    
    @field_validator('stats', mode='before')
    @classmethod
    def parse_stats(cls, v):
        """Parse stats from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v if v is not None else {}


# URL discovery schemas
class DiscoveredUrlResponse(BaseModel):
    """Schema for discovered URL response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
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
    
    id: int
    url_id: int
    form_action: Optional[str]
    form_method: Optional[str]
    form_fields: Dict[str, Any]
    csrf_tokens: List[str]
    authentication_required: bool
    
    @field_validator('form_fields', mode='before')
    @classmethod
    def parse_form_fields(cls, v):
        """Parse form_fields from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v if v is not None else {}
    
    @field_validator('csrf_tokens', mode='before')
    @classmethod
    def parse_csrf_tokens(cls, v):
        """Parse csrf_tokens from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []


# Technology fingerprint schemas
class TechnologyFingerprintResponse(BaseModel):
    """Schema for technology fingerprint response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    url_id: int
    server_software: Optional[str]
    programming_language: Optional[str]
    framework: Optional[str]
    cms: Optional[str]
    javascript_libraries: List[str]
    security_headers: Dict[str, str]
    detected_at: datetime
    
    @field_validator('javascript_libraries', mode='before')
    @classmethod
    def parse_javascript_libraries(cls, v):
        """Parse javascript_libraries from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    @field_validator('security_headers', mode='before')
    @classmethod
    def parse_security_headers(cls, v):
        """Parse security_headers from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v if v is not None else {}


# Summary schemas
class ProjectSummary(BaseModel):
    """Summary information for a project."""
    id: int
    name: str
    target_domain: str
    total_scans: int
    last_scan_date: Optional[datetime]
    total_urls_discovered: int
    total_forms_found: int


class ScanSummary(BaseModel):
    """Summary information for a scan session."""
    id: int
    project_id: int
    status: ScanStatus
    start_time: datetime
    end_time: Optional[datetime]
    urls_discovered: int
    forms_extracted: int
    technologies_detected: int


# Pagination and filtering
class PaginationParams(BaseModel):
    """Pagination parameters."""
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ScanSessionFilter(BaseModel):
    """Filter parameters for scan sessions."""
    status: Optional[ScanStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class UrlDiscoveryFilter(BaseModel):
    """Filter parameters for discovered URLs."""
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    method: Optional[str] = None


# Dashboard overview
class DashboardOverview(BaseModel):
    """Dashboard overview data."""
    total_projects: int
    total_scans: int
    active_scans: int
    total_urls_discovered: int
    total_forms_found: int
    total_technologies_detected: int
    recent_projects: List[ProjectSummary]
    recent_scans: List[ScanSummary]


# Real-time update schemas
class ScanProgressUpdate(BaseModel):
    """Schema for scan progress updates."""
    scan_id: int
    status: ScanStatus
    progress_percentage: float = Field(ge=0, le=100)
    urls_discovered: int
    current_url: Optional[str]
    message: Optional[str]


class RealTimeUpdate(BaseModel):
    """Schema for real-time updates."""
    type: str  # 'scan_progress', 'scan_complete', 'url_discovered', etc.
    data: Dict[str, Any]
    timestamp: datetime


# Metrics schemas
class MetricSummary(BaseModel):
    """Summary metrics for dashboard."""
    name: str
    value: float
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # 'up', 'down', 'stable'


class DashboardMetricCreate(BaseModel):
    """Schema for creating dashboard metrics."""
    name: str
    value: float
    metadata: Optional[Dict[str, Any]] = None


class DashboardMetricUpdate(BaseModel):
    """Schema for updating dashboard metrics."""
    value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class DashboardMetricResponse(BaseModel):
    """Schema for dashboard metric response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    value: float
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    @field_validator('metadata', mode='before')
    @classmethod
    def parse_metadata(cls, v):
        """Parse metadata from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v if v is not None else {}