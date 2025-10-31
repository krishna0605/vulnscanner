-- =====================================================
-- ENHANCED VULNERABILITY SCANNER - COMPLETE SCHEMA
-- =====================================================
-- Combined schema file for Supabase PostgreSQL database
-- This file combines all schema components in proper execution order
-- 
-- Execution Order:
-- 1. Extensions and Types
-- 2. Core Tables (Users, Auth, System)
-- 3. Project Tables
-- 4. Scanning Tables
-- 5. Vulnerability Tables
-- 6. Reporting Tables
-- 7. Integration Tables
-- 8. Row Level Security Policies
-- 9. Indexes and Constraints
-- 10. Security Fixes
-- =====================================================

-- =====================================================
-- PART 1: EXTENSIONS AND TYPES
-- =====================================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- CUSTOM ENUM TYPES
-- =====================================================

-- User role enumeration
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'admin',
        'user',
        'viewer'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Project visibility enumeration
DO $$ BEGIN
    CREATE TYPE project_visibility AS ENUM (
        'private',
        'team',
        'public'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Scan status enumeration
DO $$ BEGIN
    CREATE TYPE scan_status AS ENUM (
        'pending',
        'queued',
        'running',
        'paused',
        'completed',
        'failed',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Scan type enumeration
DO $$ BEGIN
    CREATE TYPE scan_type AS ENUM (
        'discovery',
        'vulnerability',
        'full',
        'custom'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Queue status enumeration
DO $$ BEGIN
    CREATE TYPE queue_status AS ENUM (
        'pending',
        'processing',
        'completed',
        'failed',
        'retrying'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- HTTP method enumeration
DO $$ BEGIN
    CREATE TYPE http_method AS ENUM (
        'GET',
        'POST',
        'PUT',
        'DELETE',
        'PATCH',
        'HEAD',
        'OPTIONS'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Severity level enumeration
DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM (
        'info',
        'low',
        'medium',
        'high',
        'critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Vulnerability category enumeration
DO $$ BEGIN
    CREATE TYPE vulnerability_category AS ENUM (
        'injection',
        'authentication',
        'authorization',
        'exposure',
        'configuration',
        'cryptography',
        'business_logic',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Vulnerability status enumeration
DO $$ BEGIN
    CREATE TYPE vulnerability_status AS ENUM (
        'open',
        'confirmed',
        'false_positive',
        'fixed',
        'accepted_risk',
        'duplicate'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Report format enumeration
DO $$ BEGIN
    CREATE TYPE report_format AS ENUM (
        'pdf',
        'html',
        'json',
        'csv',
        'xml'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Notification type enumeration
DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM (
        'scan_completed',
        'vulnerability_found',
        'scan_failed',
        'project_shared',
        'system_alert',
        'report_ready'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Integration type enumeration
DO $$ BEGIN
    CREATE TYPE integration_type AS ENUM (
        'slack',
        'email',
        'webhook',
        'jira',
        'github',
        'gitlab',
        'teams'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =====================================================
-- PART 2: CORE TABLES
-- =====================================================

-- User profiles table (extends auth.users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    email VARCHAR(255),
    avatar_url TEXT,
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    email_verified BOOLEAN DEFAULT FALSE,
    phone VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
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
    permissions JSONB DEFAULT '[]'::jsonb,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User sessions for tracking active sessions
CREATE TABLE public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscription plans and billing
CREATE TABLE public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage tracking for billing
CREATE TABLE public.usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE CASCADE,
    metric_name VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    billing_period_start TIMESTAMPTZ NOT NULL,
    billing_period_end TIMESTAMPTZ NOT NULL
);

-- System settings
CREATE TABLE public.system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Background jobs tracking
CREATE TABLE public.background_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payload JSONB,
    result JSONB,
    error_message TEXT,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity logs for audit trail
CREATE TABLE public.activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TRIGGERS AND FUNCTIONS FOR CORE TABLES
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to handle new user registration
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Triggers for updated_at columns
DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_api_keys_updated_at ON public.api_keys;
CREATE TRIGGER update_api_keys_updated_at
    BEFORE UPDATE ON public.api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_sessions_updated_at ON public.user_sessions;
CREATE TRIGGER update_user_sessions_updated_at
    BEFORE UPDATE ON public.user_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_system_settings_updated_at ON public.system_settings;
CREATE TRIGGER update_system_settings_updated_at
    BEFORE UPDATE ON public.system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for new user registration
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- =====================================================
-- INITIAL DATA FOR CORE TABLES
-- =====================================================

-- Insert default system settings
INSERT INTO public.system_settings (key, value, description, is_public) VALUES
('max_concurrent_scans', '10', 'Maximum number of concurrent scans per user', true),
('default_scan_timeout', '3600', 'Default scan timeout in seconds', true),
('max_crawl_depth', '10', 'Maximum crawl depth allowed', true),
('rate_limit_requests_per_minute', '100', 'API rate limit per minute', true),
('maintenance_mode', 'false', 'System maintenance mode flag', true);

-- =====================================================
-- PART 3: PROJECT TABLES
-- =====================================================

-- Projects table
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    target_domain VARCHAR(255) NOT NULL,
    scope_rules JSONB DEFAULT '[]'::jsonb,
    visibility project_visibility DEFAULT 'private',
    is_active BOOLEAN DEFAULT TRUE,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project members for collaboration
CREATE TABLE public.project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',
    permissions JSONB DEFAULT '[]'::jsonb,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    invited_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    UNIQUE(project_id, user_id)
);

-- Project settings
CREATE TABLE public.project_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE UNIQUE,
    scan_schedule JSONB,
    notification_settings JSONB DEFAULT '{}'::jsonb,
    security_settings JSONB DEFAULT '{}'::jsonb,
    integration_settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scan configurations templates
CREATE TABLE public.scan_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project invitations
CREATE TABLE public.project_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    token VARCHAR(255) NOT NULL UNIQUE,
    invited_by UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project comments for collaboration
CREATE TABLE public.project_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES public.project_comments(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project favorites
CREATE TABLE public.project_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, project_id)
);

-- Project activity tracking
CREATE TABLE public.project_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project statistics
CREATE TABLE public.project_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE UNIQUE,
    total_scans INTEGER DEFAULT 0,
    total_vulnerabilities INTEGER DEFAULT 0,
    last_scan_at TIMESTAMPTZ,
    avg_scan_duration INTERVAL,
    total_urls_discovered INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TRIGGERS AND FUNCTIONS FOR PROJECT TABLES
-- =====================================================

-- Function to add project owner as member
CREATE OR REPLACE FUNCTION add_project_owner_as_member()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.project_members (project_id, user_id, role)
    VALUES (NEW.id, NEW.owner_id, 'owner');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to generate invitation token
CREATE OR REPLACE FUNCTION generate_invitation_token()
RETURNS TRIGGER AS $$
BEGIN
    NEW.token = encode(gen_random_bytes(32), 'hex');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for project tables
DROP TRIGGER IF EXISTS update_projects_updated_at ON public.projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_project_settings_updated_at ON public.project_settings;
CREATE TRIGGER update_project_settings_updated_at
    BEFORE UPDATE ON public.project_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_scan_configurations_updated_at ON public.scan_configurations;
CREATE TRIGGER update_scan_configurations_updated_at
    BEFORE UPDATE ON public.scan_configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_project_comments_updated_at ON public.project_comments;
CREATE TRIGGER update_project_comments_updated_at
    BEFORE UPDATE ON public.project_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_project_statistics_updated_at ON public.project_statistics;
CREATE TRIGGER update_project_statistics_updated_at
    BEFORE UPDATE ON public.project_statistics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS add_owner_as_member ON public.projects;
CREATE TRIGGER add_owner_as_member
    AFTER INSERT ON public.projects
    FOR EACH ROW EXECUTE FUNCTION add_project_owner_as_member();

DROP TRIGGER IF EXISTS generate_invitation_token_trigger ON public.project_invitations;
CREATE TRIGGER generate_invitation_token_trigger
    BEFORE INSERT ON public.project_invitations
    FOR EACH ROW EXECUTE FUNCTION generate_invitation_token();

-- =====================================================
-- VIEWS FOR PROJECT TABLES
-- =====================================================

-- Project members with user details
CREATE VIEW project_members_with_users AS
SELECT 
    pm.id,
    pm.project_id,
    pm.user_id,
    pm.role,
    pm.permissions,
    pm.joined_at,
    p.username,
    p.full_name,
    p.avatar_url
FROM public.project_members pm
JOIN public.profiles p ON pm.user_id = p.id;

-- Project overview with statistics
CREATE VIEW project_overview AS
SELECT 
    p.id,
    p.name,
    p.description,
    p.target_domain,
    p.owner_id,
    p.visibility,
    p.is_active,
    p.created_at,
    p.updated_at,
    ps.total_scans,
    ps.total_vulnerabilities,
    ps.last_scan_at,
    ps.avg_scan_duration,
    ps.total_urls_discovered
FROM public.projects p
LEFT JOIN public.project_statistics ps ON p.id = ps.project_id;

-- =====================================================
-- PART 4: SCANNING TABLES
-- =====================================================

-- Scan sessions
CREATE TABLE public.scan_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100),
    status scan_status DEFAULT 'pending',
    scan_type scan_type DEFAULT 'full',
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    statistics JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crawl queue for URL discovery
CREATE TABLE public.crawl_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    url_hash VARCHAR(64) NOT NULL,
    parent_url TEXT,
    depth INTEGER DEFAULT 0,
    method http_method DEFAULT 'GET',
    headers JSONB DEFAULT '{}'::jsonb,
    body TEXT,
    priority INTEGER DEFAULT 0,
    status queue_status DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Discovered URLs
CREATE TABLE public.discovered_urls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    url_hash VARCHAR(64) NOT NULL,
    parent_url TEXT,
    method http_method DEFAULT 'GET',
    status_code INTEGER,
    content_type VARCHAR(100),
    content_length INTEGER,
    response_time INTEGER,
    page_title VARCHAR(500),
    meta_description TEXT,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, url_hash)
);

-- URL metadata and analysis
CREATE TABLE public.url_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    headers JSONB DEFAULT '{}'::jsonb,
    cookies JSONB DEFAULT '[]'::jsonb,
    forms_count INTEGER DEFAULT 0,
    links_count INTEGER DEFAULT 0,
    images_count INTEGER DEFAULT 0,
    scripts_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Extracted forms
CREATE TABLE public.extracted_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    form_action TEXT,
    form_method http_method DEFAULT 'GET',
    form_enctype VARCHAR(50),
    fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    csrf_tokens JSONB DEFAULT '[]'::jsonb,
    authentication_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Form fields details
CREATE TABLE public.form_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_id UUID REFERENCES public.extracted_forms(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    field_value TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    validation_pattern TEXT,
    placeholder TEXT,
    max_length INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Technology fingerprints
CREATE TABLE public.technology_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    server_software VARCHAR(100),
    programming_language VARCHAR(50),
    framework VARCHAR(100),
    cms VARCHAR(100),
    javascript_libraries JSONB DEFAULT '[]'::jsonb,
    css_frameworks JSONB DEFAULT '[]'::jsonb,
    analytics_tools JSONB DEFAULT '[]'::jsonb,
    security_tools JSONB DEFAULT '[]'::jsonb,
    version_info JSONB DEFAULT '{}'::jsonb,
    confidence DECIMAL(3,2) DEFAULT 0.0,
    details JSONB DEFAULT '{}'::jsonb,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security headers analysis
CREATE TABLE public.security_headers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    content_security_policy TEXT,
    strict_transport_security TEXT,
    x_frame_options VARCHAR(50),
    x_content_type_options VARCHAR(50),
    x_xss_protection VARCHAR(50),
    referrer_policy VARCHAR(50),
    permissions_policy TEXT,
    cross_origin_embedder_policy VARCHAR(50),
    cross_origin_opener_policy VARCHAR(50),
    cross_origin_resource_policy VARCHAR(50),
    security_score INTEGER,
    missing_headers JSONB DEFAULT '[]'::jsonb,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crawl metrics and performance
CREATE TABLE public.crawl_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    urls_discovered INTEGER DEFAULT 0,
    urls_processed INTEGER DEFAULT 0,
    urls_failed INTEGER DEFAULT 0,
    avg_response_time DECIMAL(10,2),
    total_data_transferred BIGINT DEFAULT 0,
    crawl_rate DECIMAL(10,2),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crawl errors and issues
CREATE TABLE public.crawl_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    error_type VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    status_code INTEGER,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- Robots.txt policies
CREATE TABLE public.robots_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    robots_txt_content TEXT,
    allowed_paths TEXT[],
    disallowed_paths TEXT[],
    crawl_delay INTEGER,
    sitemap_urls TEXT[],
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scheduled scans
CREATE TABLE public.scheduled_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    configuration JSONB NOT NULL,
    schedule_expression VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TRIGGERS AND FUNCTIONS FOR SCANNING TABLES
-- =====================================================

-- Function to update scan statistics
CREATE OR REPLACE FUNCTION update_scan_statistics()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE public.scan_sessions 
        SET statistics = jsonb_build_object(
            'urls_discovered', (SELECT COUNT(*) FROM public.discovered_urls WHERE session_id = NEW.id),
            'forms_found', (SELECT COUNT(*) FROM public.extracted_forms ef JOIN public.discovered_urls du ON ef.url_id = du.id WHERE du.session_id = NEW.id),
            'technologies_detected', (SELECT COUNT(*) FROM public.technology_fingerprints tf JOIN public.discovered_urls du ON tf.url_id = du.id WHERE du.session_id = NEW.id),
            'duration_seconds', EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time))
        )
        WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to normalize URLs
CREATE OR REPLACE FUNCTION normalize_url(input_url TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Basic URL normalization
    input_url := LOWER(TRIM(input_url));
    
    -- Remove trailing slash
    IF input_url LIKE '%/' AND input_url NOT LIKE '%://' THEN
        input_url := LEFT(input_url, LENGTH(input_url) - 1);
    END IF;
    
    RETURN input_url;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate next scheduled run
CREATE OR REPLACE FUNCTION calculate_next_run()
RETURNS TRIGGER AS $$
BEGIN
    -- Simple cron-like calculation (basic implementation)
    -- In production, use a proper cron parser
    NEW.next_run_at := NOW() + INTERVAL '1 day';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for scanning tables
DROP TRIGGER IF EXISTS update_scan_sessions_updated_at ON public.scan_sessions;
CREATE TRIGGER update_scan_sessions_updated_at
    BEFORE UPDATE ON public.scan_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_scheduled_scans_updated_at ON public.scheduled_scans;
CREATE TRIGGER update_scheduled_scans_updated_at
    BEFORE UPDATE ON public.scheduled_scans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_scan_statistics_trigger ON public.scan_sessions;
CREATE TRIGGER update_scan_statistics_trigger
    AFTER UPDATE ON public.scan_sessions
    FOR EACH ROW EXECUTE FUNCTION update_scan_statistics();

DROP TRIGGER IF EXISTS calculate_next_run_trigger ON public.scheduled_scans;
CREATE TRIGGER calculate_next_run_trigger
    BEFORE INSERT OR UPDATE ON public.scheduled_scans
    FOR EACH ROW EXECUTE FUNCTION calculate_next_run();

-- =====================================================
-- VIEWS FOR SCANNING TABLES
-- =====================================================

-- Active scans view
CREATE VIEW active_scans AS
SELECT 
    ss.id,
    ss.project_id,
    ss.name,
    ss.status,
    ss.scan_type,
    ss.start_time,
    ss.configuration,
    ss.statistics,
    p.name as project_name,
    p.target_domain
FROM public.scan_sessions ss
JOIN public.projects p ON ss.project_id = p.id
WHERE ss.status IN ('pending', 'queued', 'running', 'paused');

-- URL discovery summary
CREATE VIEW url_discovery_summary AS
SELECT 
    du.session_id,
    COUNT(*) as total_urls,
    COUNT(CASE WHEN du.status_code BETWEEN 200 AND 299 THEN 1 END) as successful_urls,
    COUNT(CASE WHEN du.status_code BETWEEN 400 AND 499 THEN 1 END) as client_error_urls,
    COUNT(CASE WHEN du.status_code BETWEEN 500 AND 599 THEN 1 END) as server_error_urls,
    AVG(du.response_time) as avg_response_time,
    SUM(du.content_length) as total_content_length
FROM public.discovered_urls du
GROUP BY du.session_id;

-- Technology summary
CREATE VIEW technology_summary AS
SELECT 
    tf.session_id,
    tf.server_software,
    tf.programming_language,
    tf.framework,
    tf.cms,
    COUNT(*) as detection_count,
    AVG(tf.confidence) as avg_confidence
FROM public.technology_fingerprints tf
JOIN public.discovered_urls du ON tf.url_id = du.id
GROUP BY tf.session_id, tf.server_software, tf.programming_language, tf.framework, tf.cms;

-- =====================================================
-- PART 5: VULNERABILITY TABLES
-- =====================================================

-- Vulnerability types and definitions
CREATE TABLE public.vulnerability_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    category vulnerability_category NOT NULL,
    severity severity_level NOT NULL,
    cwe_id INTEGER,
    owasp_category VARCHAR(50),
    description TEXT NOT NULL,
    impact TEXT,
    remediation TEXT,
    reference_links JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Discovered vulnerabilities
CREATE TABLE public.vulnerabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE SET NULL,
    form_id UUID REFERENCES public.extracted_forms(id) ON DELETE SET NULL,
    vulnerability_type_id UUID REFERENCES public.vulnerability_types(id) ON DELETE RESTRICT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity severity_level NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.0,
    impact_score DECIMAL(3,1) DEFAULT 0.0,
    exploitability_score DECIMAL(3,1) DEFAULT 0.0,
    cvss_vector VARCHAR(100),
    cvss_score DECIMAL(3,1),
    status vulnerability_status DEFAULT 'open',
    false_positive BOOLEAN DEFAULT FALSE,
    risk_score DECIMAL(3,1),
    evidence JSONB DEFAULT '{}'::jsonb,
    proof_of_concept TEXT,
    remediation_guidance TEXT,
    assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ,
    fixed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability instances for tracking multiple occurrences
CREATE TABLE public.vulnerability_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id UUID REFERENCES public.vulnerabilities(id) ON DELETE CASCADE,
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    parameter VARCHAR(100),
    payload TEXT,
    response_evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SSL/TLS certificate analysis
CREATE TABLE public.ssl_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    issuer VARCHAR(255),
    subject VARCHAR(255),
    serial_number VARCHAR(100),
    signature_algorithm VARCHAR(50),
    public_key_algorithm VARCHAR(50),
    key_size INTEGER,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    is_expired BOOLEAN DEFAULT FALSE,
    is_self_signed BOOLEAN DEFAULT FALSE,
    is_wildcard BOOLEAN DEFAULT FALSE,
    san_domains TEXT[],
    certificate_chain JSONB DEFAULT '[]'::jsonb,
    vulnerabilities JSONB DEFAULT '[]'::jsonb,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- DNS records analysis
CREATE TABLE public.dns_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    record_type VARCHAR(10) NOT NULL,
    record_value TEXT NOT NULL,
    ttl INTEGER,
    priority INTEGER,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- HTTP security analysis
CREATE TABLE public.http_security_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    supports_https BOOLEAN DEFAULT FALSE,
    enforces_https BOOLEAN DEFAULT FALSE,
    hsts_enabled BOOLEAN DEFAULT FALSE,
    hsts_max_age INTEGER,
    hsts_include_subdomains BOOLEAN DEFAULT FALSE,
    secure_cookies BOOLEAN DEFAULT FALSE,
    httponly_cookies BOOLEAN DEFAULT FALSE,
    samesite_cookies VARCHAR(20),
    mixed_content_issues JSONB DEFAULT '[]'::jsonb,
    insecure_forms JSONB DEFAULT '[]'::jsonb,
    security_score INTEGER,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability comments and notes
CREATE TABLE public.vulnerability_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id UUID REFERENCES public.vulnerabilities(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability assignments and workflow
CREATE TABLE public.vulnerability_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id UUID REFERENCES public.vulnerabilities(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    due_date TIMESTAMPTZ,
    priority INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability remediation tracking
CREATE TABLE public.vulnerability_remediations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id UUID REFERENCES public.vulnerabilities(id) ON DELETE CASCADE,
    remediation_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    implemented_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    implementation_date TIMESTAMPTZ,
    verification_notes TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability trends and analytics
CREATE TABLE public.vulnerability_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    vulnerability_type_id UUID REFERENCES public.vulnerability_types(id) ON DELETE CASCADE,
    severity severity_level NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    trend_period VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability patterns and signatures
CREATE TABLE public.vulnerability_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_type_id UUID REFERENCES public.vulnerability_types(id) ON DELETE CASCADE,
    pattern_name VARCHAR(100) NOT NULL,
    pattern_regex TEXT,
    pattern_description TEXT,
    confidence_weight DECIMAL(3,2) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Compliance frameworks mapping
CREATE TABLE public.compliance_frameworks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(20),
    description TEXT,
    requirements JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability compliance mapping
CREATE TABLE public.vulnerability_compliance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id UUID REFERENCES public.vulnerabilities(id) ON DELETE CASCADE,
    framework_id UUID REFERENCES public.compliance_frameworks(id) ON DELETE CASCADE,
    requirement_id VARCHAR(50) NOT NULL,
    compliance_status VARCHAR(20) DEFAULT 'non_compliant',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TRIGGERS AND FUNCTIONS FOR VULNERABILITY TABLES
-- =====================================================

-- Function to calculate risk score
DROP FUNCTION IF EXISTS calculate_risk_score(numeric,numeric,numeric);
CREATE OR REPLACE FUNCTION calculate_risk_score(
    impact_score DECIMAL,
    exploitability_score DECIMAL,
    confidence DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN ROUND((impact_score * exploitability_score * confidence) / 10, 1);
END;
$$ LANGUAGE plpgsql;

-- Function to update vulnerability trends
CREATE OR REPLACE FUNCTION update_vulnerability_trends()
RETURNS TRIGGER AS $$
DECLARE
    project_uuid UUID;
BEGIN
    -- Get project ID from session
    SELECT project_id INTO project_uuid
    FROM public.scan_sessions
    WHERE id = NEW.session_id;
    
    -- Update daily trends
    INSERT INTO public.vulnerability_trends (
        project_id, vulnerability_type_id, severity, count, 
        trend_period, period_start, period_end
    )
    VALUES (
        project_uuid, NEW.vulnerability_type_id, NEW.severity, 1,
        'daily', DATE_TRUNC('day', NOW()), DATE_TRUNC('day', NOW()) + INTERVAL '1 day'
    )
    ON CONFLICT (project_id, vulnerability_type_id, severity, trend_period, period_start)
    DO UPDATE SET count = vulnerability_trends.count + 1;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to auto-assign severity based on type
CREATE OR REPLACE FUNCTION auto_assign_severity()
RETURNS TRIGGER AS $$
DECLARE
    default_severity severity_level;
BEGIN
    SELECT severity INTO default_severity
    FROM public.vulnerability_types
    WHERE id = NEW.vulnerability_type_id;
    
    IF NEW.severity IS NULL THEN
        NEW.severity := default_severity;
    END IF;
    
    -- Calculate risk score
    NEW.risk_score := calculate_risk_score(
        COALESCE(NEW.impact_score, 5.0),
        COALESCE(NEW.exploitability_score, 5.0),
        COALESCE(NEW.confidence, 0.5)
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for vulnerability tables
DROP TRIGGER IF EXISTS update_vulnerability_types_updated_at ON public.vulnerability_types;
CREATE TRIGGER update_vulnerability_types_updated_at
    BEFORE UPDATE ON public.vulnerability_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_vulnerabilities_updated_at ON public.vulnerabilities;
CREATE TRIGGER update_vulnerabilities_updated_at
    BEFORE UPDATE ON public.vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_vulnerability_comments_updated_at ON public.vulnerability_comments;
CREATE TRIGGER update_vulnerability_comments_updated_at
    BEFORE UPDATE ON public.vulnerability_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_vulnerability_patterns_updated_at ON public.vulnerability_patterns;
CREATE TRIGGER update_vulnerability_patterns_updated_at
    BEFORE UPDATE ON public.vulnerability_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_vulnerability_trends_trigger ON public.vulnerabilities;
CREATE TRIGGER update_vulnerability_trends_trigger
    AFTER INSERT ON public.vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION update_vulnerability_trends();

DROP TRIGGER IF EXISTS auto_assign_severity_trigger ON public.vulnerabilities;
CREATE TRIGGER auto_assign_severity_trigger
    BEFORE INSERT ON public.vulnerabilities
    FOR EACH ROW EXECUTE FUNCTION auto_assign_severity();

-- =====================================================
-- VIEWS FOR VULNERABILITY TABLES
-- =====================================================

-- Vulnerability summary view
CREATE VIEW vulnerability_summary AS
SELECT 
    v.id,
    v.session_id,
    v.url_id,
    v.vulnerability_type_id,
    v.title,
    v.description,
    v.severity,
    v.confidence,
    v.impact_score,
    v.exploitability_score,
    v.status,
    v.assigned_to,
    v.created_at,
    vt.name as vulnerability_type,
    vt.category,
    ss.project_id,
    du.url
FROM public.vulnerabilities v
JOIN public.vulnerability_types vt ON v.vulnerability_type_id = vt.id
JOIN public.scan_sessions ss ON v.session_id = ss.id
LEFT JOIN public.discovered_urls du ON v.url_id = du.id;

-- Recent vulnerabilities view
CREATE VIEW recent_vulnerabilities AS
SELECT 
    v.id,
    v.title,
    v.severity,
    v.status,
    v.created_at,
    vt.name as vulnerability_type,
    vt.category,
    ss.project_id,
    p.name as project_name,
    du.url
FROM public.vulnerabilities v
JOIN public.vulnerability_types vt ON v.vulnerability_type_id = vt.id
JOIN public.scan_sessions ss ON v.session_id = ss.id
JOIN public.projects p ON ss.project_id = p.id
LEFT JOIN public.discovered_urls du ON v.url_id = du.id
WHERE v.created_at >= NOW() - INTERVAL '30 days'
ORDER BY v.created_at DESC;

-- Security metrics view
CREATE VIEW security_metrics AS
SELECT 
    du.url,
    regexp_replace(du.url, '^https?://([^/]+).*', '\1') as domain,
    COUNT(v.id) as vulnerability_count,
    AVG(v.impact_score) as avg_impact_score,
    COUNT(CASE WHEN v.severity = 'critical' THEN 1 END) as critical_vulnerabilities,
    COUNT(CASE WHEN v.severity = 'high' THEN 1 END) as high_vulnerabilities,
    COUNT(CASE WHEN v.severity = 'medium' THEN 1 END) as medium_vulnerabilities,
    COUNT(CASE WHEN v.severity = 'low' THEN 1 END) as low_vulnerabilities,
    ss.project_id
FROM public.discovered_urls du
JOIN public.scan_sessions ss ON du.session_id = ss.id
LEFT JOIN public.vulnerabilities v ON du.id = v.url_id
GROUP BY du.url, ss.project_id;

-- =====================================================
-- PART 6: REPORTING TABLES
-- =====================================================

-- Scan reports
CREATE TABLE public.scan_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    format report_format NOT NULL,
    template_id UUID,
    summary TEXT,
    content JSONB,
    file_path TEXT,
    file_size BIGINT,
    generated_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    download_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Report schedules for automated reporting
CREATE TABLE public.report_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL,
    format report_format NOT NULL,
    template_id UUID,
    schedule_expression VARCHAR(100) NOT NULL,
    recipients JSONB DEFAULT '[]'::jsonb,
    filters JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dashboard metrics for real-time analytics
CREATE TABLE public.dashboard_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    dimensions JSONB DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Report templates
CREATE TABLE public.report_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    format report_format NOT NULL,
    template_content JSONB NOT NULL,
    css_styles TEXT,
    is_system_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics events for tracking user behavior
CREATE TABLE public.analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE public.performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Export jobs for large data exports
CREATE TABLE public.export_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL,
    format report_format NOT NULL,
    filters JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'pending',
    file_path TEXT,
    file_size BIGINT,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR REPORTING TABLES
-- =====================================================

CREATE INDEX idx_scan_reports_session_id ON public.scan_reports(session_id);
CREATE INDEX idx_scan_reports_generated_at ON public.scan_reports(generated_at);
CREATE INDEX idx_report_schedules_project_id ON public.report_schedules(project_id);
CREATE INDEX idx_report_schedules_next_run ON public.report_schedules(next_run_at) WHERE is_active = TRUE;
CREATE INDEX idx_dashboard_metrics_project_id ON public.dashboard_metrics(project_id);
CREATE INDEX idx_dashboard_metrics_recorded_at ON public.dashboard_metrics(recorded_at);
CREATE INDEX idx_analytics_events_user_id ON public.analytics_events(user_id);
CREATE INDEX idx_analytics_events_created_at ON public.analytics_events(created_at);
CREATE INDEX idx_performance_metrics_recorded_at ON public.performance_metrics(recorded_at);
CREATE INDEX idx_export_jobs_user_id ON public.export_jobs(user_id);
CREATE INDEX idx_export_jobs_status ON public.export_jobs(status);

-- =====================================================
-- TRIGGERS AND FUNCTIONS FOR REPORTING TABLES
-- =====================================================

-- Function to calculate next run time for reports
CREATE OR REPLACE FUNCTION calculate_next_run_time(schedule_expr TEXT)
RETURNS TIMESTAMPTZ AS $$
BEGIN
    -- Simple implementation - in production use a proper cron parser
    CASE schedule_expr
        WHEN '@daily' THEN RETURN DATE_TRUNC('day', NOW()) + INTERVAL '1 day';
        WHEN '@weekly' THEN RETURN DATE_TRUNC('week', NOW()) + INTERVAL '1 week';
        WHEN '@monthly' THEN RETURN DATE_TRUNC('month', NOW()) + INTERVAL '1 month';
        ELSE RETURN NOW() + INTERVAL '1 day';
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- Function to update schedule next run
CREATE OR REPLACE FUNCTION update_schedule_next_run()
RETURNS TRIGGER AS $$
BEGIN
    NEW.next_run_at := calculate_next_run_time(NEW.schedule_expression);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to record dashboard metrics
CREATE OR REPLACE FUNCTION record_dashboard_metric(
    p_project_id UUID,
    p_metric_name VARCHAR,
    p_metric_value DECIMAL,
    p_metric_type VARCHAR,
    p_dimensions JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.dashboard_metrics (
        project_id, metric_name, metric_value, metric_type, dimensions, expires_at
    ) VALUES (
        p_project_id, p_metric_name, p_metric_value, p_metric_type, p_dimensions,
        NOW() + INTERVAL '30 days'
    );
END;
$$ LANGUAGE plpgsql;

-- Function to refresh analytics views
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY project_analytics_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY vulnerability_trends_summary;
END;
$$ LANGUAGE plpgsql;

-- Triggers for reporting tables
DROP TRIGGER IF EXISTS update_report_schedules_updated_at ON public.report_schedules;
CREATE TRIGGER update_report_schedules_updated_at
    BEFORE UPDATE ON public.report_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_report_templates_updated_at ON public.report_templates;
CREATE TRIGGER update_report_templates_updated_at
    BEFORE UPDATE ON public.report_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_schedule_next_run_trigger ON public.report_schedules;
CREATE TRIGGER update_schedule_next_run_trigger
    BEFORE INSERT OR UPDATE ON public.report_schedules
    FOR EACH ROW EXECUTE FUNCTION update_schedule_next_run();

-- =====================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- =====================================================

-- Project analytics summary
CREATE MATERIALIZED VIEW project_analytics_summary AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    COUNT(DISTINCT ss.id) as total_scans,
    COUNT(DISTINCT v.id) as total_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'critical') as critical_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'high') as high_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'medium') as medium_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'low') as low_vulnerabilities,
    COUNT(DISTINCT du.id) as total_urls_discovered,
    COUNT(DISTINCT ef.id) as total_forms_found,
    COUNT(DISTINCT tf.id) as total_technologies_detected,
    MAX(ss.start_time) as last_scan_date,
    AVG(EXTRACT(EPOCH FROM (ss.end_time - ss.start_time))) as avg_scan_duration
FROM public.projects p
LEFT JOIN public.scan_sessions ss ON p.id = ss.project_id
LEFT JOIN public.vulnerabilities v ON ss.id = v.session_id
LEFT JOIN public.discovered_urls du ON ss.id = du.session_id
LEFT JOIN public.extracted_forms ef ON du.id = ef.url_id
LEFT JOIN public.technology_fingerprints tf ON du.id = tf.url_id
GROUP BY p.id, p.name;

CREATE UNIQUE INDEX idx_project_analytics_summary_project_id 
ON project_analytics_summary(project_id);

-- Vulnerability trends summary
CREATE MATERIALIZED VIEW vulnerability_trends_summary AS
SELECT 
    vt.project_id,
    vt.vulnerability_type_id,
    vty.name as vulnerability_type_name,
    vty.category,
    vt.severity,
    vt.trend_period,
    DATE_TRUNC(vt.trend_period::TEXT, vt.period_start) as period,
    SUM(vt.count) as total_count,
    AVG(vt.count) as avg_count
FROM public.vulnerability_trends vt
JOIN public.vulnerability_types vty ON vt.vulnerability_type_id = vty.id
GROUP BY vt.project_id, vt.vulnerability_type_id, vty.name, vty.category, 
         vt.severity, vt.trend_period, DATE_TRUNC(vt.trend_period::TEXT, vt.period_start);

CREATE UNIQUE INDEX idx_vulnerability_trends_summary_unique 
ON vulnerability_trends_summary(project_id, vulnerability_type_id, severity, trend_period, period);

-- =====================================================
-- INITIAL DATA FOR REPORTING TABLES
-- =====================================================

-- Insert default report templates
INSERT INTO public.report_templates (name, description, template_type, format, template_content, is_system_template) VALUES
('Executive Summary', 'High-level security overview for executives', 'executive', 'pdf', '{"sections": ["summary", "risk_overview", "recommendations"]}', TRUE),
('Technical Report', 'Detailed technical findings for security teams', 'technical', 'pdf', '{"sections": ["vulnerabilities", "technical_details", "remediation"]}', TRUE),
('Compliance Report', 'Compliance-focused report for auditors', 'compliance', 'pdf', '{"sections": ["compliance_status", "findings", "evidence"]}', TRUE),
('Quick Summary', 'Brief overview in JSON format', 'summary', 'json', '{"sections": ["stats", "critical_findings"]}', TRUE);

-- =====================================================
-- PART 7: INTEGRATION TABLES
-- =====================================================

-- Notifications
CREATE TABLE public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- External integrations
CREATE TABLE public.integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    type integration_type NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMPTZ,
    sync_status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhooks
CREATE TABLE public.webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    secret VARCHAR(255),
    events TEXT[] NOT NULL DEFAULT '{}',
    headers JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook delivery tracking
CREATE TABLE public.webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES public.webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    response_headers JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    attempted_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    error_message TEXT
);

-- Email templates
CREATE TABLE public.email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_type VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    html_content TEXT NOT NULL,
    text_content TEXT,
    variables JSONB DEFAULT '[]'::jsonb,
    is_system_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User notification preferences
CREATE TABLE public.notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    email_enabled BOOLEAN DEFAULT TRUE,
    push_enabled BOOLEAN DEFAULT TRUE,
    slack_enabled BOOLEAN DEFAULT FALSE,
    frequency VARCHAR(20) DEFAULT 'immediate',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, notification_type)
);

-- API rate limiting
CREATE TABLE public.api_rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    request_count INTEGER DEFAULT 0,
    window_start TIMESTAMPTZ NOT NULL,
    window_duration INTERVAL DEFAULT '1 hour',
    limit_per_window INTEGER DEFAULT 1000,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- External API credentials
CREATE TABLE public.external_api_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    integration_id UUID REFERENCES public.integrations(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    credentials JSONB NOT NULL, -- Encrypted
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integration logs
CREATE TABLE public.integration_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES public.integrations(id) ON DELETE CASCADE,
    webhook_id UUID REFERENCES public.webhooks(id) ON DELETE SET NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    log_level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR INTEGRATION TABLES
-- =====================================================

CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX idx_notifications_project_id ON public.notifications(project_id);
CREATE INDEX idx_notifications_type ON public.notifications(type);
CREATE INDEX idx_notifications_is_read ON public.notifications(is_read);
CREATE INDEX idx_notifications_created_at ON public.notifications(created_at);

CREATE INDEX idx_integrations_project_id ON public.integrations(project_id);
CREATE INDEX idx_integrations_user_id ON public.integrations(user_id);
CREATE INDEX idx_integrations_type ON public.integrations(type);
CREATE INDEX idx_integrations_is_active ON public.integrations(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_webhooks_project_id ON public.webhooks(project_id);
CREATE INDEX idx_webhooks_user_id ON public.webhooks(user_id);
CREATE INDEX idx_webhooks_is_active ON public.webhooks(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_webhook_deliveries_webhook_id ON public.webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_status ON public.webhook_deliveries(status);
CREATE INDEX idx_webhook_deliveries_attempted_at ON public.webhook_deliveries(attempted_at);

CREATE INDEX idx_email_templates_template_type ON public.email_templates(template_type);
CREATE INDEX idx_email_templates_is_system ON public.email_templates(is_system_template);
CREATE INDEX idx_email_templates_created_by ON public.email_templates(created_by);

CREATE INDEX idx_notification_preferences_user_id ON public.notification_preferences(user_id);
CREATE INDEX idx_notification_preferences_notification_type ON public.notification_preferences(notification_type);

CREATE INDEX idx_api_rate_limits_user_id ON public.api_rate_limits(user_id);
CREATE INDEX idx_api_rate_limits_endpoint ON public.api_rate_limits(endpoint);
CREATE INDEX idx_api_rate_limits_window_start ON public.api_rate_limits(window_start);

CREATE INDEX idx_external_api_credentials_integration_id ON public.external_api_credentials(integration_id);
CREATE INDEX idx_external_api_credentials_provider ON public.external_api_credentials(provider);

CREATE INDEX idx_integration_logs_integration_id ON public.integration_logs(integration_id);
CREATE INDEX idx_integration_logs_webhook_id ON public.integration_logs(webhook_id);
CREATE INDEX idx_integration_logs_timestamp ON public.integration_logs(timestamp);

-- =====================================================
-- TRIGGERS AND FUNCTIONS FOR INTEGRATION TABLES
-- =====================================================

-- Function to create notification
CREATE OR REPLACE FUNCTION create_notification(
    p_user_id UUID,
    p_project_id UUID,
    p_type notification_type,
    p_title VARCHAR,
    p_message TEXT,
    p_data JSONB DEFAULT '{}'
)
RETURNS UUID AS $$
DECLARE
    notification_id UUID;
BEGIN
    INSERT INTO public.notifications (user_id, project_id, type, title, message, data)
    VALUES (p_user_id, p_project_id, p_type, p_title, p_message, p_data)
    RETURNING id INTO notification_id;
    
    RETURN notification_id;
END;
$$ LANGUAGE plpgsql;

-- Function to mark notification as read
CREATE OR REPLACE FUNCTION mark_notification_read(notification_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.notifications 
    SET is_read = TRUE, read_at = NOW()
    WHERE id = notification_id;
END;
$$ LANGUAGE plpgsql;

-- Function to trigger webhook
CREATE OR REPLACE FUNCTION trigger_webhook(
    p_webhook_id UUID,
    p_event_type VARCHAR,
    p_payload JSONB
)
RETURNS UUID AS $$
DECLARE
    delivery_id UUID;
BEGIN
    INSERT INTO public.webhook_deliveries (webhook_id, event_type, payload)
    VALUES (p_webhook_id, p_event_type, p_payload)
    RETURNING id INTO delivery_id;
    
    RETURN delivery_id;
END;
$$ LANGUAGE plpgsql;

-- Function to check API rate limit
CREATE OR REPLACE FUNCTION check_api_rate_limit(
    p_user_id UUID,
    p_endpoint VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    current_count INTEGER;
    rate_limit INTEGER;
BEGIN
    SELECT request_count, limit_per_window 
    INTO current_count, rate_limit
    FROM public.api_rate_limits
    WHERE user_id = p_user_id 
    AND endpoint = p_endpoint
    AND window_start > NOW() - window_duration;
    
    IF current_count IS NULL THEN
        INSERT INTO public.api_rate_limits (user_id, endpoint, request_count, window_start)
        VALUES (p_user_id, p_endpoint, 1, NOW());
        RETURN TRUE;
    END IF;
    
    IF current_count >= rate_limit THEN
        RETURN FALSE;
    END IF;
    
    UPDATE public.api_rate_limits 
    SET request_count = request_count + 1
    WHERE user_id = p_user_id AND endpoint = p_endpoint;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Triggers for integration tables
DROP TRIGGER IF EXISTS update_integrations_updated_at ON public.integrations;
CREATE TRIGGER update_integrations_updated_at
    BEFORE UPDATE ON public.integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_webhooks_updated_at ON public.webhooks;
CREATE TRIGGER update_webhooks_updated_at
    BEFORE UPDATE ON public.webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_email_templates_updated_at ON public.email_templates;
CREATE TRIGGER update_email_templates_updated_at
    BEFORE UPDATE ON public.email_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notification_preferences_updated_at ON public.notification_preferences;
CREATE TRIGGER update_notification_preferences_updated_at
    BEFORE UPDATE ON public.notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_external_api_credentials_updated_at ON public.external_api_credentials;
CREATE TRIGGER update_external_api_credentials_updated_at
    BEFORE UPDATE ON public.external_api_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INITIAL DATA FOR INTEGRATION TABLES
-- =====================================================

-- Insert default email templates
INSERT INTO public.email_templates (template_type, name, subject, html_content, text_content, variables, is_system_template) VALUES
('scan_completed', 'Scan Completed', 'Security Scan Completed - {{project_name}}', 
 '<h1>Scan Completed</h1><p>Your security scan for {{project_name}} has completed.</p><p>{{vulnerability_count}} vulnerabilities found.</p>', 
 'Scan Completed\n\nYour security scan for {{project_name}} has completed.\n{{vulnerability_count}} vulnerabilities found.',
 '["project_name", "vulnerability_count", "scan_duration"]', TRUE),

('vulnerability_found', 'Critical Vulnerability Found', 'Critical Vulnerability Detected - {{project_name}}',
 '<h1>Critical Vulnerability Detected</h1><p>A critical vulnerability has been found in {{project_name}}.</p><p>Vulnerability: {{vulnerability_title}}</p>',
 'Critical Vulnerability Detected\n\nA critical vulnerability has been found in {{project_name}}.\nVulnerability: {{vulnerability_title}}',
 '["project_name", "vulnerability_title", "severity", "url"]', TRUE),

('scan_failed', 'Scan Failed', 'Security Scan Failed - {{project_name}}',
 '<h1>Scan Failed</h1><p>Your security scan for {{project_name}} has failed.</p><p>Error: {{error_message}}</p>',
 'Scan Failed\n\nYour security scan for {{project_name}} has failed.\nError: {{error_message}}',
 '["project_name", "error_message"]', TRUE);

-- =====================================================
-- PART 8: ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.background_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_statistics ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.scan_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crawl_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.discovered_urls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.url_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.form_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.technology_fingerprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_headers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crawl_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crawl_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.robots_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheduled_scans ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.vulnerability_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ssl_certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dns_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.http_security_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_remediations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.compliance_frameworks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_compliance ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.scan_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dashboard_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.export_jobs ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_rate_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.external_api_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.integration_logs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS HELPER FUNCTIONS
-- =====================================================

-- Function to check if user is a project member
CREATE OR REPLACE FUNCTION is_project_member(project_id UUID, user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.project_members 
        WHERE project_id = $1 AND user_id = $2
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is project owner
CREATE OR REPLACE FUNCTION is_project_owner(project_id UUID, user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.projects 
        WHERE id = $1 AND owner_id = $2
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has specific project role
CREATE OR REPLACE FUNCTION has_project_role(project_id UUID, user_id UUID, required_role user_role)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.project_members 
        WHERE project_id = $1 AND user_id = $2 AND role >= required_role
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = $1 AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has project access
CREATE OR REPLACE FUNCTION user_has_project_access(project_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.project_members pm
        JOIN public.projects p ON p.id = pm.project_id
        WHERE pm.project_id = $1 
        AND pm.user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION user_is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = auth.uid() AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- RLS POLICIES FOR CORE TABLES
-- =====================================================

-- Profiles policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles"
    ON public.profiles FOR SELECT
    USING (is_admin(auth.uid()));

-- API Keys policies
CREATE POLICY "Users can manage their own API keys"
    ON public.api_keys FOR ALL
    USING (auth.uid() = user_id);

-- User Sessions policies
CREATE POLICY "Users can view their own sessions"
    ON public.user_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own sessions"
    ON public.user_sessions FOR UPDATE
    USING (auth.uid() = user_id);

-- Subscriptions policies
CREATE POLICY "Users can view their own subscriptions"
    ON public.subscriptions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage all subscriptions"
    ON public.subscriptions FOR ALL
    USING (is_admin(auth.uid()));

-- Usage Records policies
CREATE POLICY "Users can view their own usage records"
    ON public.usage_records FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all usage records"
    ON public.usage_records FOR SELECT
    USING (is_admin(auth.uid()));

-- System Settings policies
CREATE POLICY "Admins can manage system settings"
    ON public.system_settings FOR ALL
    USING (is_admin(auth.uid()));

CREATE POLICY "Users can view public system settings"
    ON public.system_settings FOR SELECT
    USING (is_public = TRUE);

-- Background Jobs policies
CREATE POLICY "Users can view their own background jobs"
    ON public.background_jobs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all background jobs"
    ON public.background_jobs FOR SELECT
    USING (is_admin(auth.uid()));

-- Activity Logs policies
CREATE POLICY "Users can view their own activity logs"
    ON public.activity_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all activity logs"
    ON public.activity_logs FOR SELECT
    USING (is_admin(auth.uid()));

-- =====================================================
-- RLS POLICIES FOR PROJECT TABLES
-- =====================================================

-- Projects policies
CREATE POLICY "Users can view projects they are members of"
    ON public.projects FOR SELECT
    USING (is_project_member(id, auth.uid()) OR visibility = 'public');

CREATE POLICY "Users can create projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Project owners can update their projects"
    ON public.projects FOR UPDATE
    USING (is_project_owner(id, auth.uid()));

CREATE POLICY "Project owners can delete their projects"
    ON public.projects FOR DELETE
    USING (is_project_owner(id, auth.uid()));

-- Project Members policies
CREATE POLICY "Project members can view project membership"
    ON public.project_members FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project owners can manage project members"
    ON public.project_members FOR ALL
    USING (is_project_owner(project_id, auth.uid()));

-- Project Settings policies
CREATE POLICY "Project members can view project settings"
    ON public.project_settings FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project owners can manage project settings"
    ON public.project_settings FOR ALL
    USING (is_project_owner(project_id, auth.uid()));

-- Scan Configurations policies
CREATE POLICY "Project members can view scan configurations"
    ON public.scan_configurations FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project members with editor role can manage scan configurations"
    ON public.scan_configurations FOR ALL
    USING (has_project_role(project_id, auth.uid(), 'editor'));

-- Project Invitations policies
CREATE POLICY "Project owners can manage invitations"
    ON public.project_invitations FOR ALL
    USING (is_project_owner(project_id, auth.uid()));

CREATE POLICY "Invited users can view their invitations"
    ON public.project_invitations FOR SELECT
    USING (auth.jwt() ->> 'email' = invited_email);

-- Project Comments policies
CREATE POLICY "Project members can view comments"
    ON public.project_comments FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project members can create comments"
    ON public.project_comments FOR INSERT
    WITH CHECK (is_project_member(project_id, auth.uid()) AND auth.uid() = user_id);

CREATE POLICY "Users can update their own comments"
    ON public.project_comments FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own comments or project owners can delete any"
    ON public.project_comments FOR DELETE
    USING (auth.uid() = user_id OR is_project_owner(project_id, auth.uid()));

-- Project Favorites policies
CREATE POLICY "Users can manage their own favorites"
    ON public.project_favorites FOR ALL
    USING (auth.uid() = user_id);

-- Project Activity policies
CREATE POLICY "Project members can view project activity"
    ON public.project_activity FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

-- Project Statistics policies
CREATE POLICY "Project members can view project statistics"
    ON public.project_statistics FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

-- =====================================================
-- RLS POLICIES FOR SCANNING TABLES
-- =====================================================

-- Scan Sessions policies
CREATE POLICY "Project members can view scan sessions"
    ON public.scan_sessions FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project members with editor role can manage scan sessions"
    ON public.scan_sessions FOR ALL
    USING (has_project_role(project_id, auth.uid(), 'editor'));

-- Crawl Queue policies
CREATE POLICY "Project members can view crawl queue for their project scans"
    ON public.crawl_queue FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.scan_sessions ss 
        WHERE ss.id = session_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Discovered URLs policies
CREATE POLICY "Project members can view discovered URLs for their project scans"
    ON public.discovered_urls FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.scan_sessions ss 
        WHERE ss.id = session_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- URL Metadata policies
CREATE POLICY "Project members can view URL metadata for their project URLs"
    ON public.url_metadata FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE du.id = url_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Extracted Forms policies
CREATE POLICY "Project members can view extracted forms for their project URLs"
    ON public.extracted_forms FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE du.id = url_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Form Fields policies
CREATE POLICY "Project members can view form fields for their project forms"
    ON public.form_fields FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.extracted_forms ef
        JOIN public.discovered_urls du ON du.id = ef.url_id
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE ef.id = form_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Technology Fingerprints policies
CREATE POLICY "Project members can view technology fingerprints for their project URLs"
    ON public.technology_fingerprints FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE du.id = url_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Security Headers policies
CREATE POLICY "Project members can view security headers for their project URLs"
    ON public.security_headers FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE du.id = url_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Crawl Metrics policies
CREATE POLICY "Project members can view crawl metrics for their project scans"
    ON public.crawl_metrics FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.scan_sessions ss 
        WHERE ss.id = session_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Crawl Errors policies
CREATE POLICY "Project members can view crawl errors for their project scans"
    ON public.crawl_errors FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.scan_sessions ss 
        WHERE ss.id = session_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Robots Policies policies
CREATE POLICY "Anyone can view robots policies"
    ON public.robots_policies FOR SELECT
    USING (TRUE);

-- Scheduled Scans policies
CREATE POLICY "Project members can view scheduled scans"
    ON public.scheduled_scans FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project members with editor role can manage scheduled scans"
    ON public.scheduled_scans FOR ALL
    USING (has_project_role(project_id, auth.uid(), 'editor'));

-- =====================================================
-- RLS POLICIES FOR VULNERABILITY TABLES
-- =====================================================

-- Vulnerability Types policies
CREATE POLICY "Authenticated users can view vulnerability types"
    ON public.vulnerability_types FOR SELECT
    USING (auth.role() = 'authenticated');

-- Vulnerabilities policies
CREATE POLICY "Project members can view vulnerabilities for their project scans"
    ON public.vulnerabilities FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.scan_sessions ss 
        WHERE ss.id = session_id AND is_project_member(ss.project_id, auth.uid())
    ));

CREATE POLICY "Project members with editor role can manage vulnerabilities"
    ON public.vulnerabilities FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.scan_sessions ss 
        WHERE ss.id = session_id AND has_project_role(ss.project_id, auth.uid(), 'editor')
    ));

-- Vulnerability Instances policies
CREATE POLICY "Project members can view vulnerability instances"
    ON public.vulnerability_instances FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- SSL Certificates policies
CREATE POLICY "Project members can view SSL certificates for their project URLs"
    ON public.ssl_certificates FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE du.id = url_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- DNS Records policies
CREATE POLICY "Project members can view DNS records for their project URLs"
    ON public.dns_records FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE du.id = url_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- HTTP Security Analysis policies
CREATE POLICY "Project members can view HTTP security analysis for their project URLs"
    ON public.http_security_analysis FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON ss.id = du.session_id
        WHERE du.id = url_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Vulnerability Comments policies
CREATE POLICY "Project members can view vulnerability comments"
    ON public.vulnerability_comments FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND is_project_member(ss.project_id, auth.uid())
    ));

CREATE POLICY "Project members can create vulnerability comments"
    ON public.vulnerability_comments FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND is_project_member(ss.project_id, auth.uid())
    ) AND auth.uid() = user_id);

-- Vulnerability Assignments policies
CREATE POLICY "Project members can view vulnerability assignments"
    ON public.vulnerability_assignments FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND is_project_member(ss.project_id, auth.uid())
    ));

CREATE POLICY "Project members with editor role can manage vulnerability assignments"
    ON public.vulnerability_assignments FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND has_project_role(ss.project_id, auth.uid(), 'editor')
    ));

-- Vulnerability Remediations policies
CREATE POLICY "Project members can view vulnerability remediations"
    ON public.vulnerability_remediations FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND is_project_member(ss.project_id, auth.uid())
    ));

CREATE POLICY "Project members with editor role can manage vulnerability remediations"
    ON public.vulnerability_remediations FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND has_project_role(ss.project_id, auth.uid(), 'editor')
    ));

-- Vulnerability Trends policies
CREATE POLICY "Project members can view vulnerability trends for their projects"
    ON public.vulnerability_trends FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

-- Vulnerability Patterns policies
CREATE POLICY "Project members can view vulnerability patterns for their projects"
    ON public.vulnerability_patterns FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

-- Compliance Frameworks policies
CREATE POLICY "Authenticated users can view compliance frameworks"
    ON public.compliance_frameworks FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage compliance frameworks"
    ON public.compliance_frameworks FOR ALL
    USING (is_admin(auth.uid()));

-- Vulnerability Compliance policies
CREATE POLICY "Project members can view vulnerability compliance for their projects"
    ON public.vulnerability_compliance FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.vulnerabilities v
        JOIN public.scan_sessions ss ON ss.id = v.session_id
        WHERE v.id = vulnerability_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- =====================================================
-- RLS POLICIES FOR REPORTING TABLES
-- =====================================================

-- Scan Reports policies
CREATE POLICY "Project members can view scan reports for their projects"
    ON public.scan_reports FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project members with editor role can manage scan reports"
    ON public.scan_reports FOR ALL
    USING (has_project_role(project_id, auth.uid(), 'editor'));

-- Report Schedules policies
CREATE POLICY "Project members can view report schedules for their projects"
    ON public.report_schedules FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project members with editor role can manage report schedules"
    ON public.report_schedules FOR ALL
    USING (has_project_role(project_id, auth.uid(), 'editor'));

-- Dashboard Metrics policies
CREATE POLICY "Project members can view dashboard metrics for their projects"
    ON public.dashboard_metrics FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

-- Report Templates policies
CREATE POLICY "Users can view public report templates"
    ON public.report_templates FOR SELECT
    USING (is_public = TRUE OR auth.uid() = created_by);

CREATE POLICY "Users can create their own report templates"
    ON public.report_templates FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update their own report templates"
    ON public.report_templates FOR UPDATE
    USING (auth.uid() = created_by);

CREATE POLICY "Users can delete their own report templates"
    ON public.report_templates FOR DELETE
    USING (auth.uid() = created_by);

-- Analytics Events policies
CREATE POLICY "Project members can view analytics events for their projects"
    ON public.analytics_events FOR SELECT
    USING (project_id IS NULL OR is_project_member(project_id, auth.uid()));

-- Performance Metrics policies
CREATE POLICY "Project members can view performance metrics for their project scans"
    ON public.performance_metrics FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.scan_sessions ss 
        WHERE ss.id = session_id AND is_project_member(ss.project_id, auth.uid())
    ));

-- Export Jobs policies
CREATE POLICY "Users can view their own export jobs"
    ON public.export_jobs FOR SELECT
    USING (auth.uid() = created_by);

CREATE POLICY "Users can create their own export jobs"
    ON public.export_jobs FOR INSERT
    WITH CHECK (auth.uid() = created_by);

-- =====================================================
-- RLS POLICIES FOR INTEGRATION TABLES
-- =====================================================

-- Notifications policies
CREATE POLICY "Users can view their own notifications"
    ON public.notifications FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own notifications"
    ON public.notifications FOR UPDATE
    USING (auth.uid() = user_id);

-- Integrations policies
CREATE POLICY "Project members can view integrations for their projects"
    ON public.integrations FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project owners can manage integrations for their projects"
    ON public.integrations FOR ALL
    USING (is_project_owner(project_id, auth.uid()));

-- Webhooks policies
CREATE POLICY "Project members can view webhooks for their projects"
    ON public.webhooks FOR SELECT
    USING (is_project_member(project_id, auth.uid()));

CREATE POLICY "Project owners can manage webhooks for their projects"
    ON public.webhooks FOR ALL
    USING (is_project_owner(project_id, auth.uid()));

-- Webhook Deliveries policies
CREATE POLICY "Project members can view webhook deliveries for their project webhooks"
    ON public.webhook_deliveries FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.webhooks w 
        WHERE w.id = webhook_id AND is_project_member(w.project_id, auth.uid())
    ));

-- Email Templates policies
CREATE POLICY "Admins can manage email templates"
    ON public.email_templates FOR ALL
    USING (user_is_admin());

CREATE POLICY "Users can view system email templates"
    ON public.email_templates FOR SELECT
    USING (is_system_template = TRUE);

-- Notification Preferences policies
CREATE POLICY "Users can manage their own notification preferences"
    ON public.notification_preferences FOR ALL
    USING (auth.uid() = user_id);

-- API Rate Limits policies
CREATE POLICY "Users can view their own API rate limits"
    ON public.api_rate_limits FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all API rate limits"
    ON public.api_rate_limits FOR SELECT
    USING (is_admin(auth.uid()));

-- External API Credentials policies
CREATE POLICY "Users can manage their own external API credentials"
    ON public.external_api_credentials FOR ALL
    USING (auth.uid() = user_id);

-- Integration Logs policies
CREATE POLICY "Project members can view integration logs for their project integrations"
    ON public.integration_logs FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.integrations i 
        WHERE i.id = integration_id AND is_project_member(i.project_id, auth.uid())
    ));

-- =====================================================
-- PART 9: PERFORMANCE INDEXES
-- =====================================================

-- Composite indexes for complex queries
CREATE INDEX idx_project_member_access ON public.project_members(project_id, user_id, role);
CREATE INDEX idx_scan_session_analysis ON public.scan_sessions(project_id, status, start_time);
CREATE INDEX idx_url_discovery ON public.discovered_urls(session_id, status_code, discovered_at);
CREATE INDEX idx_vulnerability_analysis ON public.vulnerabilities(session_id, severity, status, created_at);
CREATE INDEX idx_security_metrics ON public.vulnerabilities(session_id, severity) WHERE status != 'resolved';
CREATE INDEX idx_reporting_data ON public.scan_reports(project_id, created_at, format);
CREATE INDEX idx_activity_tracking ON public.activity_logs(user_id, action, created_at);
CREATE INDEX idx_notification_management ON public.notifications(user_id, is_read, created_at);

-- Partial indexes for performance
CREATE INDEX idx_active_scans ON public.scan_sessions(project_id, start_time) WHERE status IN ('pending', 'running');
CREATE INDEX idx_unresolved_vulnerabilities ON public.vulnerabilities(session_id, severity, created_at) WHERE status != 'resolved';
CREATE INDEX idx_recent_activity ON public.activity_logs(user_id, created_at) WHERE created_at > NOW() - INTERVAL '30 days';
CREATE INDEX idx_active_integrations ON public.integrations(project_id, type) WHERE is_active = TRUE;
CREATE INDEX idx_failed_webhook_deliveries ON public.webhook_deliveries(webhook_id, created_at) WHERE status = 'failed';

-- GIN indexes for JSONB columns
CREATE INDEX idx_project_scope_rules_gin ON public.projects USING GIN(scope_rules);
CREATE INDEX idx_scan_configuration_gin ON public.scan_configurations USING GIN(configuration);
CREATE INDEX idx_session_statistics_gin ON public.scan_sessions USING GIN(statistics);
CREATE INDEX idx_url_metadata_gin ON public.url_metadata USING GIN(metadata);
CREATE INDEX idx_form_fields_gin ON public.form_fields USING GIN(field_data);
CREATE INDEX idx_technology_fingerprints_gin ON public.technology_fingerprints USING GIN(technologies);
CREATE INDEX idx_vulnerability_evidence_gin ON public.vulnerabilities USING GIN(evidence);
CREATE INDEX idx_integration_configuration_gin ON public.integrations USING GIN(configuration);
CREATE INDEX idx_webhook_payload_gin ON public.webhook_deliveries USING GIN(payload);

-- Text search indexes
CREATE INDEX idx_projects_text_search ON public.projects USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX idx_vulnerabilities_text_search ON public.vulnerabilities USING GIN(to_tsvector('english', title || ' ' || COALESCE(description, '')));
CREATE INDEX idx_scan_reports_text_search ON public.scan_reports USING GIN(to_tsvector('english', title || ' ' || COALESCE(summary, '')));

-- =====================================================
-- PART 10: VIEWS AND MATERIALIZED VIEWS
-- =====================================================

-- Recreate views without SECURITY DEFINER to filter data based on user project access
CREATE OR REPLACE VIEW project_members_with_users AS
SELECT 
    pm.project_id,
    pm.user_id,
    pm.role,
    pm.joined_at,
    p.username,
    p.full_name,
    p.avatar_url
FROM public.project_members pm
JOIN public.profiles p ON p.id = pm.user_id
WHERE user_has_project_access(pm.project_id);

CREATE OR REPLACE VIEW technology_summary AS
SELECT 
    tf.session_id,
    jsonb_object_agg(
        COALESCE(tf.server_software, 'unknown'),
        COUNT(*)
    ) as server_technologies,
    jsonb_object_agg(
        COALESCE(tf.programming_language, 'unknown'),
        COUNT(*)
    ) as programming_languages,
    jsonb_object_agg(
        COALESCE(tf.framework, 'unknown'),
        COUNT(*)
    ) as frameworks
FROM public.technology_fingerprints tf
JOIN public.discovered_urls du ON du.id = tf.url_id
JOIN public.scan_sessions ss ON ss.id = du.session_id
WHERE user_has_project_access(ss.project_id)
GROUP BY tf.session_id;

CREATE OR REPLACE VIEW active_scans AS
SELECT 
    ss.id,
    ss.project_id,
    ss.status,
    ss.start_time,
    ss.configuration,
    ss.statistics,
    p.name as project_name
FROM public.scan_sessions ss
JOIN public.projects p ON p.id = ss.project_id
WHERE ss.status IN ('pending', 'running')
AND user_has_project_access(ss.project_id);

CREATE OR REPLACE VIEW url_discovery_summary AS
SELECT 
    session_id,
    COUNT(*) as total_urls,
    COUNT(*) FILTER (WHERE status_code BETWEEN 200 AND 299) as success_urls,
    COUNT(*) FILTER (WHERE status_code BETWEEN 400 AND 499) as client_error_urls,
    COUNT(*) FILTER (WHERE status_code BETWEEN 500 AND 599) as server_error_urls,
    AVG(response_time) as avg_response_time
FROM public.discovered_urls du
JOIN public.scan_sessions ss ON ss.id = du.session_id
WHERE user_has_project_access(ss.project_id)
GROUP BY session_id;

CREATE OR REPLACE VIEW vulnerability_summary AS
SELECT 
    v.session_id,
    COUNT(*) as total_vulnerabilities,
    COUNT(*) FILTER (WHERE v.severity = 'critical') as critical_count,
    COUNT(*) FILTER (WHERE v.severity = 'high') as high_count,
    COUNT(*) FILTER (WHERE v.severity = 'medium') as medium_count,
    COUNT(*) FILTER (WHERE v.severity = 'low') as low_count,
    COUNT(*) FILTER (WHERE v.status = 'open') as open_count,
    COUNT(*) FILTER (WHERE v.status = 'resolved') as resolved_count
FROM public.vulnerabilities v
JOIN public.scan_sessions ss ON ss.id = v.session_id
WHERE user_has_project_access(ss.project_id)
GROUP BY v.session_id;

CREATE OR REPLACE VIEW project_overview AS
SELECT 
    p.id,
    p.name,
    p.description,
    p.target_domain,
    p.visibility,
    p.created_at,
    COUNT(DISTINCT pm.user_id) as member_count,
    COUNT(DISTINCT ss.id) as scan_count,
    COUNT(DISTINCT ss.id) FILTER (WHERE ss.status = 'completed') as completed_scans,
    MAX(ss.start_time) as last_scan_time
FROM public.projects p
LEFT JOIN public.project_members pm ON pm.project_id = p.id
LEFT JOIN public.scan_sessions ss ON ss.project_id = p.id
WHERE user_has_project_access(p.id)
GROUP BY p.id, p.name, p.description, p.target_domain, p.visibility, p.created_at;

CREATE OR REPLACE VIEW security_metrics AS
SELECT 
    ss.project_id,
    COUNT(DISTINCT v.id) as total_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'critical') as critical_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'high') as high_vulnerabilities,
    COUNT(DISTINCT du.id) as total_urls_scanned,
    COUNT(DISTINCT ef.id) as total_forms_found,
    AVG(v.risk_score) as avg_risk_score
FROM public.scan_sessions ss
LEFT JOIN public.vulnerabilities v ON v.session_id = ss.id
LEFT JOIN public.discovered_urls du ON du.session_id = ss.id
LEFT JOIN public.extracted_forms ef ON ef.url_id = du.id
WHERE user_has_project_access(ss.project_id)
GROUP BY ss.project_id;

CREATE OR REPLACE VIEW recent_vulnerabilities AS
SELECT 
    v.id,
    v.session_id,
    v.title,
    v.severity,
    v.status,
    v.risk_score,
    v.created_at,
    ss.project_id,
    p.name as project_name
FROM public.vulnerabilities v
JOIN public.scan_sessions ss ON ss.id = v.session_id
JOIN public.projects p ON p.id = ss.project_id
WHERE v.created_at > NOW() - INTERVAL '30 days'
AND user_has_project_access(ss.project_id)
ORDER BY v.created_at DESC;

-- =====================================================
-- PART 11: SECURITY FIXES AND FINAL SETUP
-- =====================================================

-- Additional security constraints
ALTER TABLE public.profiles ADD CONSTRAINT check_valid_role 
    CHECK (role IN ('user', 'admin', 'editor', 'viewer'));

ALTER TABLE public.projects ADD CONSTRAINT check_valid_visibility 
    CHECK (visibility IN ('private', 'public', 'internal'));

ALTER TABLE public.scan_sessions ADD CONSTRAINT check_valid_status 
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify RLS is enabled on all tables
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND rowsecurity = false;

-- Verify policies exist
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;

-- Verify helper functions exist
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name IN ('is_project_member', 'is_project_owner', 'has_project_role', 'is_admin', 'user_has_project_access', 'user_is_admin');

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON SCHEMA public IS 'Enhanced Vulnerability Scanner - Complete database schema with security, performance, and compliance features';

-- Table comments
COMMENT ON TABLE public.profiles IS 'User profiles extending Supabase auth.users';
COMMENT ON TABLE public.projects IS 'Security scanning projects with scope and configuration';
COMMENT ON TABLE public.scan_sessions IS 'Individual scan execution sessions';
COMMENT ON TABLE public.vulnerabilities IS 'Discovered security vulnerabilities';
COMMENT ON TABLE public.discovered_urls IS 'URLs discovered during crawling';

-- Function comments
COMMENT ON FUNCTION is_project_member(UUID, UUID) IS 'Check if user is a member of the specified project';
COMMENT ON FUNCTION is_project_owner(UUID, UUID) IS 'Check if user owns the specified project';
COMMENT ON FUNCTION has_project_role(UUID, UUID, user_role) IS 'Check if user has minimum required role in project';

-- =====================================================
-- END OF COMBINED SCHEMA
-- =====================================================