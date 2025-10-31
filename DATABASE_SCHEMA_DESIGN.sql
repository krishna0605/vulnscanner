-- =====================================================
-- Enhanced Vulnerability Scanner - Complete Database Schema
-- =====================================================
-- Designed for Supabase PostgreSQL
-- Supports: Multi-tenancy, Real-time updates, Analytics, Security scanning
-- Version: 1.0
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- ENUMS AND CUSTOM TYPES
-- =====================================================

-- User roles and permissions
CREATE TYPE user_role AS ENUM (
    'admin',
    'user',
    'viewer',
    'scanner'
);

-- Project visibility levels
CREATE TYPE project_visibility AS ENUM (
    'private',
    'team',
    'organization'
);

-- Scan session statuses
CREATE TYPE scan_status AS ENUM (
    'pending',
    'queued',
    'running',
    'paused',
    'completed',
    'failed',
    'cancelled',
    'timeout'
);

-- Scan types and modes
CREATE TYPE scan_type AS ENUM (
    'discovery',
    'vulnerability',
    'compliance',
    'full'
);

-- HTTP methods
CREATE TYPE http_method AS ENUM (
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'PATCH',
    'HEAD',
    'OPTIONS'
);

-- Vulnerability severity levels
CREATE TYPE severity_level AS ENUM (
    'info',
    'low',
    'medium',
    'high',
    'critical'
);

-- Vulnerability categories
CREATE TYPE vulnerability_category AS ENUM (
    'injection',
    'broken_auth',
    'sensitive_data',
    'xxe',
    'broken_access',
    'security_misconfig',
    'xss',
    'insecure_deserialization',
    'known_vulnerabilities',
    'insufficient_logging'
);

-- Report formats
CREATE TYPE report_format AS ENUM (
    'pdf',
    'html',
    'json',
    'csv',
    'xml'
);

-- Notification types
CREATE TYPE notification_type AS ENUM (
    'scan_complete',
    'vulnerability_found',
    'scan_failed',
    'quota_exceeded',
    'system_alert'
);

-- Integration types
CREATE TYPE integration_type AS ENUM (
    'webhook',
    'slack',
    'email',
    'jira',
    'github',
    'gitlab'
);

-- =====================================================
-- CORE USER AND AUTHENTICATION TABLES
-- =====================================================

-- User profiles (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    role user_role DEFAULT 'user',
    organization VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}'::jsonb,
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API keys for programmatic access
CREATE TABLE public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(10) NOT NULL,
    scopes JSONB DEFAULT '[]'::jsonb,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User sessions tracking
CREATE TABLE public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    location JSONB,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- PROJECT MANAGEMENT TABLES
-- =====================================================

-- Main projects table
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    target_domain VARCHAR(255) NOT NULL,
    target_urls TEXT[] DEFAULT '{}',
    scope_rules JSONB DEFAULT '[]'::jsonb,
    exclude_patterns JSONB DEFAULT '[]'::jsonb,
    visibility project_visibility DEFAULT 'private',
    settings JSONB DEFAULT '{}'::jsonb,
    tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project team members
CREATE TABLE public.project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role user_role DEFAULT 'viewer',
    permissions JSONB DEFAULT '[]'::jsonb,
    invited_by UUID REFERENCES auth.users(id),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, user_id)
);

-- Project settings and configurations
CREATE TABLE public.project_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, category)
);

-- =====================================================
-- SCANNING AND CRAWLING TABLES
-- =====================================================

-- Scan configurations (reusable templates)
CREATE TABLE public.scan_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    scan_type scan_type DEFAULT 'discovery',
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_default BOOLEAN DEFAULT false,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual scan sessions
CREATE TABLE public.scan_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    configuration_id UUID REFERENCES public.scan_configurations(id),
    name VARCHAR(100),
    status scan_status DEFAULT 'pending',
    scan_type scan_type DEFAULT 'discovery',
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    stats JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crawl queue for URLs to be processed
CREATE TABLE public.crawl_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url VARCHAR(2000) NOT NULL,
    parent_url VARCHAR(2000),
    depth INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 0,
    method http_method DEFAULT 'GET',
    headers JSONB DEFAULT '{}'::jsonb,
    body TEXT,
    retry_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Discovered URLs and their metadata
CREATE TABLE public.discovered_urls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url VARCHAR(2000) NOT NULL,
    normalized_url VARCHAR(2000),
    parent_url VARCHAR(2000),
    method http_method DEFAULT 'GET',
    status_code INTEGER,
    content_type VARCHAR(100),
    content_length INTEGER,
    response_time INTEGER,
    page_title VARCHAR(500),
    meta_description TEXT,
    headers JSONB DEFAULT '{}'::jsonb,
    cookies JSONB DEFAULT '[]'::jsonb,
    depth INTEGER DEFAULT 0,
    is_external BOOLEAN DEFAULT false,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, url, method)
);

-- URL metadata and content analysis
CREATE TABLE public.url_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    content_hash VARCHAR(64),
    word_count INTEGER,
    link_count INTEGER,
    image_count INTEGER,
    form_count INTEGER,
    script_count INTEGER,
    language VARCHAR(10),
    charset VARCHAR(50),
    robots_meta VARCHAR(100),
    canonical_url VARCHAR(2000),
    og_data JSONB DEFAULT '{}'::jsonb,
    schema_markup JSONB DEFAULT '[]'::jsonb,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- FORM ANALYSIS TABLES
-- =====================================================

-- Extracted forms from web pages
CREATE TABLE public.extracted_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    form_id VARCHAR(100),
    form_name VARCHAR(100),
    form_action VARCHAR(2000),
    form_method http_method DEFAULT 'GET',
    encoding_type VARCHAR(50),
    is_multipart BOOLEAN DEFAULT false,
    has_file_upload BOOLEAN DEFAULT false,
    csrf_tokens JSONB DEFAULT '[]'::jsonb,
    authentication_required BOOLEAN DEFAULT false,
    ssl_required BOOLEAN DEFAULT false,
    form_html TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual form fields
CREATE TABLE public.form_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_id UUID REFERENCES public.extracted_forms(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50),
    field_value TEXT,
    is_required BOOLEAN DEFAULT false,
    is_hidden BOOLEAN DEFAULT false,
    is_disabled BOOLEAN DEFAULT false,
    validation_pattern VARCHAR(500),
    placeholder_text VARCHAR(200),
    max_length INTEGER,
    min_length INTEGER,
    autocomplete VARCHAR(50),
    field_order INTEGER DEFAULT 0,
    security_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TECHNOLOGY FINGERPRINTING TABLES
-- =====================================================

-- Technology fingerprints and detection
CREATE TABLE public.technology_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    server_software VARCHAR(100),
    programming_language VARCHAR(50),
    framework VARCHAR(100),
    cms VARCHAR(100),
    database_system VARCHAR(100),
    web_server VARCHAR(100),
    javascript_libraries JSONB DEFAULT '[]'::jsonb,
    css_frameworks JSONB DEFAULT '[]'::jsonb,
    analytics_tools JSONB DEFAULT '[]'::jsonb,
    security_tools JSONB DEFAULT '[]'::jsonb,
    cdn_services JSONB DEFAULT '[]'::jsonb,
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    detection_method VARCHAR(50),
    raw_data JSONB DEFAULT '{}'::jsonb,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security headers analysis
CREATE TABLE public.security_headers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    content_security_policy TEXT,
    strict_transport_security VARCHAR(200),
    x_frame_options VARCHAR(50),
    x_content_type_options VARCHAR(50),
    x_xss_protection VARCHAR(50),
    referrer_policy VARCHAR(100),
    permissions_policy TEXT,
    cross_origin_embedder_policy VARCHAR(50),
    cross_origin_opener_policy VARCHAR(50),
    cross_origin_resource_policy VARCHAR(50),
    missing_headers JSONB DEFAULT '[]'::jsonb,
    security_score INTEGER DEFAULT 0,
    recommendations JSONB DEFAULT '[]'::jsonb,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- VULNERABILITY AND FINDINGS TABLES
-- =====================================================

-- Vulnerability types and definitions
CREATE TABLE public.vulnerability_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    category vulnerability_category NOT NULL,
    severity severity_level DEFAULT 'medium',
    description TEXT,
    impact TEXT,
    remediation TEXT,
    references JSONB DEFAULT '[]'::jsonb,
    cwe_id VARCHAR(20),
    owasp_category VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Identified vulnerabilities and security issues
CREATE TABLE public.vulnerabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url_id UUID REFERENCES public.discovered_urls(id),
    vulnerability_type_id UUID REFERENCES public.vulnerability_types(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity severity_level DEFAULT 'medium',
    confidence DECIMAL(3,2) DEFAULT 0.0,
    impact_score INTEGER DEFAULT 0,
    exploitability_score INTEGER DEFAULT 0,
    evidence JSONB DEFAULT '{}'::jsonb,
    proof_of_concept TEXT,
    remediation_steps TEXT,
    false_positive BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'open',
    assigned_to UUID REFERENCES auth.users(id),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability instances (multiple occurrences of same vuln)
CREATE TABLE public.vulnerability_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id UUID REFERENCES public.vulnerabilities(id) ON DELETE CASCADE,
    url_id UUID REFERENCES public.discovered_urls(id),
    parameter_name VARCHAR(100),
    parameter_value TEXT,
    request_data TEXT,
    response_data TEXT,
    location_details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- REPORTING AND ANALYTICS TABLES
-- =====================================================

-- Generated scan reports
CREATE TABLE public.scan_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    format report_format DEFAULT 'pdf',
    template_name VARCHAR(100),
    file_path TEXT,
    file_size INTEGER,
    download_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ,
    generated_by UUID REFERENCES auth.users(id),
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scheduled report generation
CREATE TABLE public.report_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    format report_format DEFAULT 'pdf',
    template_name VARCHAR(100),
    schedule_cron VARCHAR(100) NOT NULL,
    recipients JSONB DEFAULT '[]'::jsonb,
    filters JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dashboard metrics and analytics
CREATE TABLE public.dashboard_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_data JSONB DEFAULT '{}'::jsonb,
    time_period VARCHAR(20) DEFAULT 'daily',
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, metric_name, time_period, recorded_at)
);

-- Vulnerability trends and statistics
CREATE TABLE public.vulnerability_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_vulnerabilities INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    high_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    low_count INTEGER DEFAULT 0,
    info_count INTEGER DEFAULT 0,
    resolved_count INTEGER DEFAULT 0,
    new_count INTEGER DEFAULT 0,
    trend_data JSONB DEFAULT '{}'::jsonb,
    UNIQUE(project_id, date)
);

-- =====================================================
-- NOTIFICATION AND INTEGRATION TABLES
-- =====================================================

-- User notifications
CREATE TABLE public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    data JSONB DEFAULT '{}'::jsonb,
    is_read BOOLEAN DEFAULT false,
    is_email_sent BOOLEAN DEFAULT false,
    priority INTEGER DEFAULT 0,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- External integrations
CREATE TABLE public.integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type integration_type NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    credentials JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    sync_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook endpoints
CREATE TABLE public.webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    events JSONB DEFAULT '[]'::jsonb,
    secret_key VARCHAR(255),
    headers JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    retry_count INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    last_triggered_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook delivery logs
CREATE TABLE public.webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES public.webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    response_time INTEGER,
    attempt_count INTEGER DEFAULT 1,
    delivered_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- SYSTEM AND AUDIT TABLES
-- =====================================================

-- Activity and audit logs
CREATE TABLE public.activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    project_id UUID REFERENCES public.projects(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- System configuration and settings
CREATE TABLE public.system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,
    key VARCHAR(100) NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    updated_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(category, key)
);

-- Background job tracking
CREATE TABLE public.background_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,
    job_id VARCHAR(255) UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total INTEGER,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- BILLING AND SUBSCRIPTION TABLES (for Stripe integration)
-- =====================================================

-- User subscriptions
CREATE TABLE public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    plan_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT false,
    canceled_at TIMESTAMPTZ,
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage tracking for billing
CREATE TABLE public.usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.subscriptions(id),
    metric_name VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    billing_period_start TIMESTAMPTZ,
    billing_period_end TIMESTAMPTZ
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- Core entity indexes
CREATE INDEX idx_profiles_username ON public.profiles(username);
CREATE INDEX idx_profiles_organization ON public.profiles(organization);
CREATE INDEX idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON public.api_keys(key_hash);

-- Project and membership indexes
CREATE INDEX idx_projects_owner_id ON public.projects(owner_id);
CREATE INDEX idx_projects_target_domain ON public.projects(target_domain);
CREATE INDEX idx_projects_is_active ON public.projects(is_active);
CREATE INDEX idx_project_members_project_id ON public.project_members(project_id);
CREATE INDEX idx_project_members_user_id ON public.project_members(user_id);

-- Scan session indexes
CREATE INDEX idx_scan_sessions_project_id ON public.scan_sessions(project_id);
CREATE INDEX idx_scan_sessions_status ON public.scan_sessions(status);
CREATE INDEX idx_scan_sessions_created_by ON public.scan_sessions(created_by);
CREATE INDEX idx_scan_sessions_start_time ON public.scan_sessions(start_time);

-- URL discovery indexes
CREATE INDEX idx_discovered_urls_session_id ON public.discovered_urls(session_id);
CREATE INDEX idx_discovered_urls_parent_url ON public.discovered_urls(parent_url);
CREATE INDEX idx_discovered_urls_status_code ON public.discovered_urls(status_code);
CREATE INDEX idx_discovered_urls_content_type ON public.discovered_urls(content_type);

-- Vulnerability indexes
CREATE INDEX idx_vulnerabilities_session_id ON public.vulnerabilities(session_id);
CREATE INDEX idx_vulnerabilities_severity ON public.vulnerabilities(severity);
CREATE INDEX idx_vulnerabilities_status ON public.vulnerabilities(status);
CREATE INDEX idx_vulnerabilities_assigned_to ON public.vulnerabilities(assigned_to);

-- Analytics and reporting indexes
CREATE INDEX idx_dashboard_metrics_project_id ON public.dashboard_metrics(project_id);
CREATE INDEX idx_dashboard_metrics_recorded_at ON public.dashboard_metrics(recorded_at);
CREATE INDEX idx_vulnerability_trends_project_id ON public.vulnerability_trends(project_id);
CREATE INDEX idx_vulnerability_trends_date ON public.vulnerability_trends(date);

-- Notification and activity indexes
CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX idx_notifications_is_read ON public.notifications(is_read);
CREATE INDEX idx_activity_logs_user_id ON public.activity_logs(user_id);
CREATE INDEX idx_activity_logs_project_id ON public.activity_logs(project_id);
CREATE INDEX idx_activity_logs_created_at ON public.activity_logs(created_at);

-- Full-text search indexes
CREATE INDEX idx_discovered_urls_page_title_gin ON public.discovered_urls USING gin(to_tsvector('english', page_title));
CREATE INDEX idx_vulnerabilities_title_gin ON public.vulnerabilities USING gin(to_tsvector('english', title));
CREATE INDEX idx_vulnerabilities_description_gin ON public.vulnerabilities USING gin(to_tsvector('english', description));

-- Composite indexes for common queries
CREATE INDEX idx_scan_sessions_project_status ON public.scan_sessions(project_id, status);
CREATE INDEX idx_discovered_urls_session_status ON public.discovered_urls(session_id, status_code);
CREATE INDEX idx_vulnerabilities_session_severity ON public.vulnerabilities(session_id, severity);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.discovered_urls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.technology_fingerprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Projects policies
CREATE POLICY "Users can view their own projects"
    ON public.projects FOR SELECT
    USING (auth.uid() = owner_id OR auth.uid() IN (
        SELECT user_id FROM public.project_members WHERE project_id = id
    ));

CREATE POLICY "Users can create their own projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Project owners can update their projects"
    ON public.projects FOR UPDATE
    USING (auth.uid() = owner_id);

CREATE POLICY "Project owners can delete their projects"
    ON public.projects FOR DELETE
    USING (auth.uid() = owner_id);

-- Scan sessions policies
CREATE POLICY "Users can view scans for their projects"
    ON public.scan_sessions FOR SELECT
    USING (project_id IN (
        SELECT id FROM public.projects WHERE owner_id = auth.uid()
        UNION
        SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
    ));

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vulnerabilities_updated_at BEFORE UPDATE ON public.vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate vulnerability trends
CREATE OR REPLACE FUNCTION calculate_vulnerability_trends()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.vulnerability_trends (
        project_id,
        date,
        total_vulnerabilities,
        critical_count,
        high_count,
        medium_count,
        low_count,
        info_count
    )
    SELECT 
        s.project_id,
        CURRENT_DATE,
        COUNT(*),
        COUNT(*) FILTER (WHERE severity = 'critical'),
        COUNT(*) FILTER (WHERE severity = 'high'),
        COUNT(*) FILTER (WHERE severity = 'medium'),
        COUNT(*) FILTER (WHERE severity = 'low'),
        COUNT(*) FILTER (WHERE severity = 'info')
    FROM public.vulnerabilities v
    JOIN public.scan_sessions s ON v.session_id = s.id
    WHERE s.project_id = NEW.project_id
    GROUP BY s.project_id
    ON CONFLICT (project_id, date) DO UPDATE SET
        total_vulnerabilities = EXCLUDED.total_vulnerabilities,
        critical_count = EXCLUDED.critical_count,
        high_count = EXCLUDED.high_count,
        medium_count = EXCLUDED.medium_count,
        low_count = EXCLUDED.low_count,
        info_count = EXCLUDED.info_count;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update vulnerability trends
CREATE TRIGGER update_vulnerability_trends
    AFTER INSERT OR UPDATE OR DELETE ON public.vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION calculate_vulnerability_trends();

-- =====================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- =====================================================

-- Project summary view
CREATE MATERIALIZED VIEW project_summary AS
SELECT 
    p.id,
    p.name,
    p.target_domain,
    p.owner_id,
    COUNT(DISTINCT s.id) as total_scans,
    COUNT(DISTINCT v.id) as total_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'critical') as critical_vulns,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'high') as high_vulns,
    MAX(s.start_time) as last_scan_date,
    p.created_at
FROM public.projects p
LEFT JOIN public.scan_sessions s ON p.id = s.project_id
LEFT JOIN public.vulnerabilities v ON s.id = v.session_id
GROUP BY p.id, p.name, p.target_domain, p.owner_id, p.created_at;

-- Create unique index for materialized view
CREATE UNIQUE INDEX idx_project_summary_id ON project_summary(id);

-- Vulnerability summary view
CREATE MATERIALIZED VIEW vulnerability_summary AS
SELECT 
    v.id,
    v.title,
    v.severity,
    v.status,
    vt.category,
    s.project_id,
    u.url,
    v.created_at
FROM public.vulnerabilities v
JOIN public.vulnerability_types vt ON v.vulnerability_type_id = vt.id
JOIN public.scan_sessions s ON v.session_id = s.id
LEFT JOIN public.discovered_urls u ON v.url_id = u.id;

-- Create unique index for vulnerability summary
CREATE UNIQUE INDEX idx_vulnerability_summary_id ON vulnerability_summary(id);

-- =====================================================
-- INITIAL DATA AND SEED VALUES
-- =====================================================

-- Insert default vulnerability types (OWASP Top 10)
INSERT INTO public.vulnerability_types (name, category, severity, description, cwe_id, owasp_category) VALUES
('SQL Injection', 'injection', 'high', 'SQL injection vulnerabilities allow attackers to interfere with database queries', 'CWE-89', 'A03:2021'),
('Cross-Site Scripting (XSS)', 'xss', 'medium', 'XSS vulnerabilities allow attackers to inject malicious scripts', 'CWE-79', 'A03:2021'),
('Cross-Site Request Forgery (CSRF)', 'broken_access', 'medium', 'CSRF attacks force users to execute unwanted actions', 'CWE-352', 'A01:2021'),
('Insecure Direct Object References', 'broken_access', 'high', 'Direct access to objects without proper authorization', 'CWE-639', 'A01:2021'),
('Security Misconfiguration', 'security_misconfig', 'medium', 'Insecure default configurations and missing security headers', 'CWE-16', 'A05:2021'),
('Sensitive Data Exposure', 'sensitive_data', 'high', 'Exposure of sensitive data due to lack of encryption', 'CWE-200', 'A02:2021'),
('Missing Function Level Access Control', 'broken_access', 'medium', 'Functions not properly protected against unauthorized access', 'CWE-285', 'A01:2021'),
('Using Components with Known Vulnerabilities', 'known_vulnerabilities', 'high', 'Using outdated components with known security issues', 'CWE-1104', 'A06:2021'),
('Unvalidated Redirects and Forwards', 'broken_access', 'low', 'Redirects that can be manipulated by attackers', 'CWE-601', 'A01:2021'),
('Insufficient Logging and Monitoring', 'insufficient_logging', 'low', 'Inadequate logging and monitoring capabilities', 'CWE-778', 'A09:2021');

-- Insert default system settings
INSERT INTO public.system_settings (category, key, value, description, is_public) VALUES
('scanning', 'default_timeout', '30', 'Default request timeout in seconds', true),
('scanning', 'max_concurrent_requests', '10', 'Maximum concurrent requests per scan', true),
('scanning', 'max_depth', '5', 'Maximum crawl depth', true),
('scanning', 'respect_robots_txt', 'true', 'Whether to respect robots.txt files', true),
('security', 'password_min_length', '8', 'Minimum password length', true),
('security', 'session_timeout', '3600', 'Session timeout in seconds', false),
('notifications', 'email_enabled', 'true', 'Whether email notifications are enabled', false),
('reports', 'max_report_size', '50', 'Maximum report size in MB', false);

-- =====================================================
-- REFRESH FUNCTIONS FOR MATERIALIZED VIEWS
-- =====================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY project_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY vulnerability_summary;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON SCHEMA public IS 'Enhanced Vulnerability Scanner - Main application schema';

COMMENT ON TABLE public.profiles IS 'User profiles extending Supabase auth.users';
COMMENT ON TABLE public.projects IS 'Security scanning projects with target domains and configurations';
COMMENT ON TABLE public.scan_sessions IS 'Individual scan execution sessions with status tracking';
COMMENT ON TABLE public.discovered_urls IS 'URLs discovered during crawling with metadata';
COMMENT ON TABLE public.vulnerabilities IS 'Security vulnerabilities identified during scans';
COMMENT ON TABLE public.vulnerability_types IS 'Catalog of vulnerability types and classifications';

COMMENT ON COLUMN public.projects.scope_rules IS 'JSON array of regex patterns defining scan scope';
COMMENT ON COLUMN public.scan_sessions.configuration IS 'JSON object containing scan parameters and settings';
COMMENT ON COLUMN public.scan_sessions.stats IS 'JSON object with scan statistics (URLs found, errors, etc.)';
COMMENT ON COLUMN public.vulnerabilities.evidence IS 'JSON object containing proof and technical details';

-- =====================================================
-- END OF SCHEMA
-- =====================================================

-- To apply this schema to your Supabase project:
-- 1. Copy and paste sections into Supabase SQL Editor
-- 2. Run in order: Extensions → Types → Tables → Indexes → RLS → Functions
-- 3. Configure RLS policies for your specific access patterns
-- 4. Set up cron job to refresh materialized views:
--    SELECT cron.schedule('refresh-views', '0 */6 * * *', 'SELECT refresh_materialized_views();');