"""
Pydantic schemas for scan results including discovered URLs, forms, and technology fingerprints.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


# Base schemas for common fields
class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Discovered URL schemas
class DiscoveredURLBase(BaseModel):
    """Base schema for discovered URLs."""
    url: str = Field(..., max_length=2000, description="The discovered URL")
    parent_url: Optional[str] = Field(None, max_length=2000, description="Parent URL that led to this discovery")
    method: str = Field(default="GET", max_length=10, description="HTTP method")
    status_code: Optional[int] = Field(None, ge=100, le=599, description="HTTP status code")
    content_type: Optional[str] = Field(None, max_length=100, description="Content type from response headers")
    content_length: Optional[int] = Field(None, ge=0, description="Content length in bytes")
    response_time: Optional[int] = Field(None, ge=0, description="Response time in milliseconds")
    page_title: Optional[str] = Field(None, max_length=500, description="Page title extracted from HTML")

    @field_validator('method')
    @classmethod
    def validate_method(cls, v):
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if v.upper() not in allowed_methods:
            raise ValueError(f'Method must be one of: {", ".join(allowed_methods)}')
        return v.upper()

    @field_validator('url', 'parent_url')
    @classmethod
    def validate_url_format(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class DiscoveredURLCreate(DiscoveredURLBase):
    """Schema for creating a discovered URL."""


class DiscoveredURLUpdate(BaseModel):
    """Schema for updating a discovered URL."""
    status_code: Optional[int] = Field(None, ge=100, le=599)
    content_type: Optional[str] = Field(None, max_length=100)
    content_length: Optional[int] = Field(None, ge=0)
    response_time: Optional[int] = Field(None, ge=0)
    page_title: Optional[str] = Field(None, max_length=500)


class DiscoveredURLResponse(DiscoveredURLBase, TimestampMixin):
    """Schema for discovered URL responses."""
    id: UUID
    session_id: UUID
    discovered_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DiscoveredURLFilter(BaseModel):
    """Schema for filtering discovered URLs."""
    status_code: Optional[int] = Field(None, ge=100, le=599)
    content_type: Optional[str] = Field(None, max_length=100)
    method: Optional[str] = Field(None, max_length=10)
    url_pattern: Optional[str] = Field(None, max_length=500, description="Pattern to match in URL")
    min_response_time: Optional[int] = Field(None, ge=0)
    max_response_time: Optional[int] = Field(None, ge=0)


# Extracted Form schemas
class ExtractedFormBase(BaseModel):
    """Base schema for extracted forms."""
    form_action: Optional[str] = Field(None, max_length=2000, description="Form action URL")
    form_method: str = Field(default="POST", max_length=10, description="Form method")
    form_fields: Dict[str, Any] = Field(default_factory=dict, description="Form fields and their attributes")
    csrf_tokens: List[str] = Field(default_factory=list, description="CSRF tokens found in the form")
    authentication_required: bool = Field(default=False, description="Whether form requires authentication")

    @field_validator('form_method')
    @classmethod
    def validate_form_method(cls, v):
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if v.upper() not in allowed_methods:
            raise ValueError(f'Form method must be one of: {", ".join(allowed_methods)}')
        return v.upper()

    @field_validator('form_fields')
    @classmethod
    def validate_form_fields(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Form fields must be a dictionary')
        return v

    @field_validator('csrf_tokens')
    @classmethod
    def validate_csrf_tokens(cls, v):
        if not isinstance(v, list):
            raise ValueError('CSRF tokens must be a list')
        return v


class ExtractedFormCreate(ExtractedFormBase):
    """Schema for creating an extracted form."""
    url_id: UUID = Field(..., description="ID of the URL where this form was found")


class ExtractedFormUpdate(BaseModel):
    """Schema for updating an extracted form."""
    form_action: Optional[str] = Field(None, max_length=2000)
    form_method: Optional[str] = Field(None, max_length=10)
    form_fields: Optional[Dict[str, Any]] = None
    csrf_tokens: Optional[List[str]] = None
    authentication_required: Optional[bool] = None


class ExtractedFormResponse(ExtractedFormBase, TimestampMixin):
    """Schema for extracted form responses."""
    id: UUID
    url_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ExtractedFormFilter(BaseModel):
    """Schema for filtering extracted forms."""
    form_method: Optional[str] = Field(None, max_length=10)
    has_csrf_token: Optional[bool] = Field(None, description="Filter by presence of CSRF tokens")
    authentication_required: Optional[bool] = Field(None)
    action_pattern: Optional[str] = Field(None, max_length=500, description="Pattern to match in form action")


# Technology Fingerprint schemas
class TechnologyFingerprintBase(BaseModel):
    """Base schema for technology fingerprints."""
    server_software: Optional[str] = Field(None, max_length=100, description="Detected server software")
    programming_language: Optional[str] = Field(None, max_length=50, description="Detected programming language")
    framework: Optional[str] = Field(None, max_length=100, description="Detected web framework")
    cms: Optional[str] = Field(None, max_length=100, description="Detected content management system")
    javascript_libraries: List[str] = Field(default_factory=list, description="Detected JavaScript libraries")
    security_headers: Dict[str, str] = Field(default_factory=dict, description="Security headers found")

    @field_validator('javascript_libraries')
    @classmethod
    def validate_js_libraries(cls, v):
        if not isinstance(v, list):
            raise ValueError('JavaScript libraries must be a list')
        return v

    @field_validator('security_headers')
    @classmethod
    def validate_security_headers(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Security headers must be a dictionary')
        return v


class TechnologyFingerprintCreate(TechnologyFingerprintBase):
    """Schema for creating a technology fingerprint."""
    url_id: UUID = Field(..., description="ID of the URL where this technology was detected")


class TechnologyFingerprintUpdate(BaseModel):
    """Schema for updating a technology fingerprint."""
    server_software: Optional[str] = Field(None, max_length=100)
    programming_language: Optional[str] = Field(None, max_length=50)
    framework: Optional[str] = Field(None, max_length=100)
    cms: Optional[str] = Field(None, max_length=100)
    javascript_libraries: Optional[List[str]] = None
    security_headers: Optional[Dict[str, str]] = None


class TechnologyFingerprintResponse(TechnologyFingerprintBase, TimestampMixin):
    """Schema for technology fingerprint responses."""
    id: UUID
    url_id: UUID
    detected_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TechnologyFingerprintFilter(BaseModel):
    """Schema for filtering technology fingerprints."""
    server_software: Optional[str] = Field(None, max_length=100)
    programming_language: Optional[str] = Field(None, max_length=50)
    framework: Optional[str] = Field(None, max_length=100)
    cms: Optional[str] = Field(None, max_length=100)


# Scan Results Summary schemas
class ScanResultsSummary(BaseModel):
    """Schema for scan results summary."""
    scan_id: UUID
    total_urls: int = Field(ge=0, description="Total number of discovered URLs")
    total_forms: int = Field(ge=0, description="Total number of extracted forms")
    total_technologies: int = Field(ge=0, description="Total number of detected technologies")
    unique_domains: int = Field(ge=0, description="Number of unique domains discovered")
    status_code_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution of HTTP status codes")
    content_type_distribution: Optional[Dict[str, int]] = Field(None, description="Distribution of content types")
    technology_summary: Optional[Dict[str, List[str]]] = Field(None, description="Summary of detected technologies by type")
    security_headers_summary: Optional[Dict[str, int]] = Field(None, description="Summary of security headers found")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


# Export schemas
class ScanResultsExport(BaseModel):
    """Schema for scan results export request."""
    format: str = Field(..., pattern="^(json|csv|pdf)$", description="Export format")
    include_urls: bool = Field(default=True, description="Include discovered URLs in export")
    include_forms: bool = Field(default=True, description="Include extracted forms in export")
    include_technologies: bool = Field(default=True, description="Include technology fingerprints in export")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters to apply to export")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        allowed_formats = ['json', 'csv', 'pdf']
        if v.lower() not in allowed_formats:
            raise ValueError(f'Format must be one of: {", ".join(allowed_formats)}')
        return v.lower()


class ExportTaskResponse(BaseModel):
    """Schema for export task response."""
    task_id: str
    status: str
    scan_id: str
    format: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExportTaskStatus(BaseModel):
    """Schema for export task status."""
    task_id: str
    status: str
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage")
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    scan_id: str
    format: str
    created_at: datetime
    completed_at: Optional[datetime] = None


# Bulk operation schemas
class BulkURLCreate(BaseModel):
    """Schema for bulk URL creation."""
    urls: List[DiscoveredURLCreate] = Field(..., min_length=1, max_length=1000)

    @field_validator('urls')
    @classmethod
    def validate_urls_limit(cls, v):
        if len(v) > 1000:
            raise ValueError('Cannot create more than 1000 URLs at once')
        return v


class BulkFormCreate(BaseModel):
    """Schema for bulk form creation."""
    forms: List[ExtractedFormCreate] = Field(..., min_length=1, max_length=500)

    @field_validator('forms')
    @classmethod
    def validate_forms_limit(cls, v):
        if len(v) > 500:
            raise ValueError('Cannot create more than 500 forms at once')
        return v


class BulkTechnologyCreate(BaseModel):
    """Schema for bulk technology fingerprint creation."""
    technologies: List[TechnologyFingerprintCreate] = Field(..., min_length=1, max_length=500)

    @field_validator('technologies')
    @classmethod
    def validate_technologies_limit(cls, v):
        if len(v) > 500:
            raise ValueError('Cannot create more than 500 technology fingerprints at once')
        return v


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation response."""
    total_requested: int
    total_created: int
    total_failed: int
    errors: List[str] = Field(default_factory=list)
    created_ids: List[UUID] = Field(default_factory=list)


# Statistics schemas
class URLStatistics(BaseModel):
    """Schema for URL statistics."""
    total_urls: int
    unique_domains: int
    status_code_distribution: Dict[str, int]
    content_type_distribution: Dict[str, int]
    average_response_time: Optional[float] = None
    slowest_urls: List[Dict[str, Any]] = Field(default_factory=list)
    fastest_urls: List[Dict[str, Any]] = Field(default_factory=list)


class FormStatistics(BaseModel):
    """Schema for form statistics."""
    total_forms: int
    forms_with_csrf: int
    forms_requiring_auth: int
    method_distribution: Dict[str, int]
    most_common_fields: List[Dict[str, Any]] = Field(default_factory=list)


class TechnologyStatistics(BaseModel):
    """Schema for technology statistics."""
    total_detections: int
    unique_technologies: int
    server_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    framework_distribution: Dict[str, int]
    cms_distribution: Dict[str, int]
    security_headers_coverage: Dict[str, int]


class ComprehensiveStatistics(BaseModel):
    """Schema for comprehensive scan statistics."""
    scan_id: UUID
    url_stats: URLStatistics
    form_stats: FormStatistics
    technology_stats: TechnologyStatistics
    scan_duration: Optional[int] = Field(None, description="Scan duration in seconds")
    crawl_efficiency: Optional[float] = Field(None, description="Crawl efficiency percentage")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Common schemas
class CommonFilter(BaseModel):
    """Common filter schema for all result types."""
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at", pattern="^(created_at|url|status_code|response_time)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    scan_results_service: str
    database_connection: str
    total_urls: int
    total_forms: int
    total_technologies: int