-- =====================================================
-- ENHANCED VULNERABILITY SCANNER - SUPABASE SETUP
-- File 4: Scanning and Crawling Tables
-- =====================================================
-- Run this file AFTER 03_project_tables.sql
-- This creates scan execution, crawling, and URL discovery tables

-- =====================================================
-- SCAN EXECUTION TABLES
-- =====================================================

-- Main scan sessions table
CREATE TABLE public.scan_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    configuration_id UUID REFERENCES public.scan_configurations(id),
    name VARCHAR(100),
    description TEXT,
    scan_type scan_type DEFAULT 'discovery',
    status scan_status DEFAULT 'pending',
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    error_message TEXT,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    statistics JSONB DEFAULT '{}'::jsonb,
    progress JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES auth.users(id),
    cancelled_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crawl queue for managing URL discovery
CREATE TABLE public.crawl_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url VARCHAR(2000) NOT NULL,
    parent_url VARCHAR(2000),
    depth INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status queue_status DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Discovered URLs and their metadata
CREATE TABLE public.discovered_urls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    queue_id UUID REFERENCES public.crawl_queue(id),
    url VARCHAR(2000) NOT NULL,
    normalized_url VARCHAR(2000),
    parent_url VARCHAR(2000),
    depth INTEGER DEFAULT 0,
    method http_method DEFAULT 'GET',
    status_code INTEGER,
    content_type VARCHAR(100),
    content_length INTEGER,
    response_time INTEGER,
    redirect_url VARCHAR(2000),
    page_title VARCHAR(500),
    meta_description TEXT,
    canonical_url VARCHAR(2000),
    robots_meta VARCHAR(100),
    language VARCHAR(10),
    charset VARCHAR(50),
    last_modified TIMESTAMPTZ,
    etag VARCHAR(100),
    is_external BOOLEAN DEFAULT false,
    is_secure BOOLEAN DEFAULT false,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    last_crawled_at TIMESTAMPTZ DEFAULT NOW(),
    crawl_count INTEGER DEFAULT 1,
    UNIQUE(session_id, url, method)
);

-- URL metadata and additional information
CREATE TABLE public.url_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    metadata_type VARCHAR(50) NOT NULL,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    confidence DECIMAL(3,2) DEFAULT 1.0 CHECK (confidence BETWEEN 0 AND 1),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(url_id, metadata_type, key)
);

-- =====================================================
-- FORM AND INPUT DISCOVERY TABLES
-- =====================================================

-- Extracted forms from web pages
CREATE TABLE public.extracted_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    form_id VARCHAR(100),
    form_name VARCHAR(100),
    form_action VARCHAR(2000),
    form_method http_method DEFAULT 'POST',
    form_enctype VARCHAR(50),
    form_target VARCHAR(50),
    form_autocomplete VARCHAR(10),
    form_novalidate BOOLEAN DEFAULT false,
    csrf_token VARCHAR(500),
    csrf_field_name VARCHAR(100),
    authentication_required BOOLEAN DEFAULT false,
    is_file_upload BOOLEAN DEFAULT false,
    is_search_form BOOLEAN DEFAULT false,
    is_login_form BOOLEAN DEFAULT false,
    is_registration_form BOOLEAN DEFAULT false,
    form_html TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual form fields
CREATE TABLE public.form_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_id UUID REFERENCES public.extracted_forms(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    field_id VARCHAR(100),
    field_class VARCHAR(200),
    field_placeholder VARCHAR(200),
    field_value TEXT,
    field_required BOOLEAN DEFAULT false,
    field_readonly BOOLEAN DEFAULT false,
    field_disabled BOOLEAN DEFAULT false,
    field_hidden BOOLEAN DEFAULT false,
    field_autocomplete VARCHAR(50),
    field_pattern VARCHAR(500),
    field_min_length INTEGER,
    field_max_length INTEGER,
    field_min_value DECIMAL,
    field_max_value DECIMAL,
    field_step DECIMAL,
    field_multiple BOOLEAN DEFAULT false,
    field_accept VARCHAR(200),
    field_options JSONB DEFAULT '[]'::jsonb,
    validation_rules JSONB DEFAULT '[]'::jsonb,
    security_flags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TECHNOLOGY DETECTION TABLES
-- =====================================================

-- Technology fingerprints and detection
CREATE TABLE public.technology_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    technology_type VARCHAR(50) NOT NULL,
    technology_name VARCHAR(100) NOT NULL,
    technology_version VARCHAR(50),
    technology_category VARCHAR(50),
    confidence DECIMAL(3,2) DEFAULT 1.0 CHECK (confidence BETWEEN 0 AND 1),
    detection_method VARCHAR(50),
    evidence TEXT,
    is_outdated BOOLEAN DEFAULT false,
    has_vulnerabilities BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(url_id, technology_type, technology_name)
);

-- Security headers analysis
CREATE TABLE public.security_headers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    header_name VARCHAR(100) NOT NULL,
    header_value TEXT,
    is_present BOOLEAN DEFAULT true,
    is_secure BOOLEAN DEFAULT false,
    severity severity_level DEFAULT 'info',
    recommendation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(url_id, header_name)
);

-- =====================================================
-- CRAWL PERFORMANCE AND MONITORING
-- =====================================================

-- Crawl performance metrics
CREATE TABLE public.crawl_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,2),
    metric_unit VARCHAR(20),
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Crawl errors and issues
CREATE TABLE public.crawl_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url VARCHAR(2000),
    error_type VARCHAR(50) NOT NULL,
    error_code VARCHAR(20),
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    retry_count INTEGER DEFAULT 0,
    is_resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    severity severity_level DEFAULT 'medium',
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Robots.txt and crawl policies
CREATE TABLE public.robots_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(255) NOT NULL,
    robots_txt TEXT,
    sitemap_urls JSONB DEFAULT '[]'::jsonb,
    crawl_delay INTEGER DEFAULT 0,
    allowed_paths JSONB DEFAULT '[]'::jsonb,
    disallowed_paths JSONB DEFAULT '[]'::jsonb,
    user_agent VARCHAR(100) DEFAULT '*',
    last_fetched_at TIMESTAMPTZ DEFAULT NOW(),
    is_valid BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(domain, user_agent)
);

-- =====================================================
-- SCAN SCHEDULING AND AUTOMATION
-- =====================================================

-- Scheduled scans
CREATE TABLE public.scheduled_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    configuration_id UUID REFERENCES public.scan_configurations(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cron_expression VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT true,
    next_run_at TIMESTAMPTZ,
    last_run_at TIMESTAMPTZ,
    last_session_id UUID REFERENCES public.scan_sessions(id),
    failure_count INTEGER DEFAULT 0,
    max_failures INTEGER DEFAULT 3,
    notification_settings JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CONSTRAINTS AND CHECKS
-- =====================================================

-- Scan session constraints
ALTER TABLE public.scan_sessions 
ADD CONSTRAINT scan_sessions_name_length CHECK (char_length(name) >= 3);

ALTER TABLE public.scan_sessions 
ADD CONSTRAINT scan_sessions_valid_dates CHECK (
    (started_at IS NULL OR started_at >= created_at) AND
    (completed_at IS NULL OR completed_at >= started_at) AND
    (cancelled_at IS NULL OR cancelled_at >= created_at)
);

-- URL validation
ALTER TABLE public.discovered_urls 
ADD CONSTRAINT discovered_urls_valid_url CHECK (
    url ~ '^https?://[^\s/$.?#].[^\s]*$'
);

-- Response time validation
ALTER TABLE public.discovered_urls 
ADD CONSTRAINT discovered_urls_valid_response_time CHECK (
    response_time IS NULL OR response_time >= 0
);

-- Status code validation
ALTER TABLE public.discovered_urls 
ADD CONSTRAINT discovered_urls_valid_status_code CHECK (
    status_code IS NULL OR (status_code >= 100 AND status_code <= 599)
);

-- Form method validation
ALTER TABLE public.extracted_forms 
ADD CONSTRAINT extracted_forms_valid_method CHECK (
    form_method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
);

-- Confidence validation
ALTER TABLE public.technology_fingerprints 
ADD CONSTRAINT technology_fingerprints_valid_confidence CHECK (
    confidence BETWEEN 0 AND 1
);

-- Cron expression validation (basic check)
ALTER TABLE public.scheduled_scans 
ADD CONSTRAINT scheduled_scans_valid_cron CHECK (
    cron_expression ~ '^[0-9\*\-\,\/\s]+$'
);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_scan_sessions_updated_at 
    BEFORE UPDATE ON public.scan_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_robots_policies_updated_at 
    BEFORE UPDATE ON public.robots_policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scheduled_scans_updated_at 
    BEFORE UPDATE ON public.scheduled_scans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update scan session statistics
CREATE OR REPLACE FUNCTION update_scan_statistics()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.scan_sessions 
    SET statistics = jsonb_build_object(
        'total_urls', (SELECT COUNT(*) FROM public.discovered_urls WHERE session_id = NEW.session_id),
        'total_forms', (SELECT COUNT(*) FROM public.extracted_forms ef JOIN public.discovered_urls du ON ef.url_id = du.id WHERE du.session_id = NEW.session_id),
        'total_technologies', (SELECT COUNT(*) FROM public.technology_fingerprints tf JOIN public.discovered_urls du ON tf.url_id = du.id WHERE du.session_id = NEW.session_id),
        'updated_at', NOW()
    )
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update scan statistics when URLs are discovered
CREATE TRIGGER update_scan_stats_on_url_discovery
    AFTER INSERT ON public.discovered_urls
    FOR EACH ROW EXECUTE FUNCTION update_scan_statistics();

-- Function to normalize URLs
CREATE OR REPLACE FUNCTION normalize_url(input_url TEXT)
RETURNS TEXT AS $$
DECLARE
    normalized TEXT;
BEGIN
    -- Basic URL normalization
    normalized := lower(trim(input_url));
    
    -- Remove trailing slash for non-root paths
    IF normalized ~ '/$' AND normalized !~ '^https?://[^/]+/$' THEN
        normalized := rtrim(normalized, '/');
    END IF;
    
    -- Remove default ports
    normalized := regexp_replace(normalized, ':80/', '/', 'g');
    normalized := regexp_replace(normalized, ':443/', '/', 'g');
    
    RETURN normalized;
END;
$$ language 'plpgsql';

-- Trigger to normalize URLs on insert
CREATE OR REPLACE FUNCTION normalize_discovered_url()
RETURNS TRIGGER AS $$
BEGIN
    NEW.normalized_url := normalize_url(NEW.url);
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER normalize_url_trigger
    BEFORE INSERT OR UPDATE ON public.discovered_urls
    FOR EACH ROW EXECUTE FUNCTION normalize_discovered_url();

-- Function to calculate next scheduled run
CREATE OR REPLACE FUNCTION calculate_next_run()
RETURNS TRIGGER AS $$
BEGIN
    -- This is a simplified version - in production, use a proper cron parser
    -- For now, just add 24 hours for daily scans
    IF NEW.cron_expression LIKE '0 0 * * *' THEN
        NEW.next_run_at := COALESCE(NEW.last_run_at, NOW()) + INTERVAL '1 day';
    ELSIF NEW.cron_expression LIKE '0 * * * *' THEN
        NEW.next_run_at := COALESCE(NEW.last_run_at, NOW()) + INTERVAL '1 hour';
    ELSE
        -- Default to daily
        NEW.next_run_at := COALESCE(NEW.last_run_at, NOW()) + INTERVAL '1 day';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to calculate next run time
CREATE TRIGGER calculate_next_run_trigger
    BEFORE INSERT OR UPDATE ON public.scheduled_scans
    FOR EACH ROW EXECUTE FUNCTION calculate_next_run();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Active scan sessions with progress
CREATE VIEW active_scans AS
SELECT 
    ss.id,
    ss.project_id,
    ss.name,
    ss.scan_type,
    ss.status,
    ss.started_at,
    ss.progress,
    ss.statistics,
    p.name as project_name,
    p.target_domain,
    creator.username as created_by_username
FROM public.scan_sessions ss
JOIN public.projects p ON ss.project_id = p.id
LEFT JOIN public.profiles creator ON ss.created_by = creator.id
WHERE ss.status IN ('pending', 'running', 'paused');

-- URL discovery summary by session
CREATE VIEW url_discovery_summary AS
SELECT 
    session_id,
    COUNT(*) as total_urls,
    COUNT(CASE WHEN status_code BETWEEN 200 AND 299 THEN 1 END) as successful_urls,
    COUNT(CASE WHEN status_code BETWEEN 400 AND 499 THEN 1 END) as client_error_urls,
    COUNT(CASE WHEN status_code BETWEEN 500 AND 599 THEN 1 END) as server_error_urls,
    COUNT(CASE WHEN is_external = true THEN 1 END) as external_urls,
    AVG(response_time) as avg_response_time,
    MAX(depth) as max_depth,
    MIN(discovered_at) as first_discovery,
    MAX(discovered_at) as last_discovery
FROM public.discovered_urls
GROUP BY session_id;

-- Technology detection summary
CREATE VIEW technology_summary AS
SELECT 
    du.session_id,
    tf.technology_type,
    tf.technology_name,
    tf.technology_version,
    COUNT(*) as detection_count,
    AVG(tf.confidence) as avg_confidence,
    COUNT(CASE WHEN tf.has_vulnerabilities = true THEN 1 END) as vulnerable_instances
FROM public.technology_fingerprints tf
JOIN public.discovered_urls du ON tf.url_id = du.id
GROUP BY du.session_id, tf.technology_type, tf.technology_name, tf.technology_version;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.scan_sessions IS 'Main scan execution sessions with configuration and status';
COMMENT ON TABLE public.crawl_queue IS 'Queue for managing URL crawling and discovery';
COMMENT ON TABLE public.discovered_urls IS 'All URLs discovered during scanning with metadata';
COMMENT ON TABLE public.url_metadata IS 'Additional metadata for discovered URLs';
COMMENT ON TABLE public.extracted_forms IS 'HTML forms extracted from web pages';
COMMENT ON TABLE public.form_fields IS 'Individual form fields with validation and security info';
COMMENT ON TABLE public.technology_fingerprints IS 'Detected technologies and frameworks';
COMMENT ON TABLE public.security_headers IS 'Security header analysis results';
COMMENT ON TABLE public.crawl_metrics IS 'Performance metrics for crawl sessions';
COMMENT ON TABLE public.crawl_errors IS 'Errors and issues encountered during crawling';
COMMENT ON TABLE public.robots_policies IS 'Robots.txt policies and crawl restrictions';
COMMENT ON TABLE public.scheduled_scans IS 'Automated scan scheduling configuration';

COMMENT ON COLUMN public.scan_sessions.configuration IS 'JSON object with scan parameters and settings';
COMMENT ON COLUMN public.scan_sessions.statistics IS 'JSON object with scan execution statistics';
COMMENT ON COLUMN public.scan_sessions.progress IS 'JSON object with current scan progress information';
COMMENT ON COLUMN public.discovered_urls.normalized_url IS 'Normalized version of URL for deduplication';
COMMENT ON COLUMN public.form_fields.field_options IS 'JSON array of select/radio options';
COMMENT ON COLUMN public.form_fields.validation_rules IS 'JSON array of client-side validation rules';
COMMENT ON COLUMN public.form_fields.security_flags IS 'JSON array of security-related flags';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment these to verify tables were created successfully:

-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('scan_sessions', 'crawl_queue', 'discovered_urls', 'extracted_forms');
-- SELECT * FROM active_scans LIMIT 5;
-- SELECT * FROM url_discovery_summary LIMIT 5;

-- =====================================================
-- NEXT STEPS
-- =====================================================
-- After running this file successfully:
-- 1. Run 05_vulnerability_tables.sql for vulnerability management
-- 2. Run 06_reporting_tables.sql for reports and analytics
-- 3. Continue with remaining table creation files
-- 4. Apply RLS policies with 08_rls_policies.sql