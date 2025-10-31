-- =====================================================
-- 06_reporting_tables.sql
-- Reporting, Analytics, and Dashboard Tables
-- =====================================================

-- Scan Reports Table
-- Stores generated reports for scan sessions
CREATE TABLE public.scan_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    report_type public.report_format NOT NULL DEFAULT 'pdf',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_path TEXT, -- Supabase Storage path
    file_size INTEGER,
    generated_by UUID REFERENCES auth.users(id),
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    download_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Report Schedules Table
-- Automated report generation schedules
CREATE TABLE public.report_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    report_type public.report_format NOT NULL DEFAULT 'pdf',
    schedule_cron VARCHAR(100) NOT NULL, -- Cron expression
    recipients TEXT[] DEFAULT '{}', -- Email addresses
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    run_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dashboard Metrics Table
-- Real-time metrics for dashboard widgets
CREATE TABLE public.dashboard_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- 'scan_count', 'vulnerability_count', 'url_count', etc.
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit VARCHAR(20), -- 'count', 'percentage', 'bytes', 'seconds'
    time_period VARCHAR(20) DEFAULT 'current', -- 'current', 'daily', 'weekly', 'monthly'
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Composite unique constraint to prevent duplicates
    UNIQUE(project_id, metric_type, metric_name, time_period, recorded_at)
);

-- Report Templates Table
-- Customizable report templates
CREATE TABLE public.report_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    template_type public.report_format NOT NULL,
    template_content JSONB NOT NULL, -- Template configuration
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics Events Table
-- Track user actions and system events for analytics
CREATE TABLE public.analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    project_id UUID REFERENCES public.projects(id) ON DELETE SET NULL,
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL, -- 'scan_started', 'vulnerability_found', 'report_generated'
    event_name VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance Metrics Table
-- System performance and resource usage metrics
CREATE TABLE public.performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_category VARCHAR(50) NOT NULL, -- 'system', 'database', 'crawler', 'api'
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    metric_unit VARCHAR(20), -- 'ms', 'mb', 'percent', 'count'
    instance_id VARCHAR(100), -- Server/worker instance identifier
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Export Jobs Table
-- Track data export operations
CREATE TABLE public.export_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL, -- 'vulnerabilities', 'urls', 'full_report'
    export_format public.report_format NOT NULL,
    filters JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    file_path TEXT, -- Supabase Storage path
    file_size INTEGER,
    download_url TEXT,
    expires_at TIMESTAMPTZ,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CONSTRAINTS AND INDEXES
-- =====================================================

-- Scan Reports Indexes
CREATE INDEX idx_scan_reports_session ON public.scan_reports(session_id);
CREATE INDEX idx_scan_reports_type ON public.scan_reports(report_type);
CREATE INDEX idx_scan_reports_generated_at ON public.scan_reports(generated_at);
CREATE INDEX idx_scan_reports_generated_by ON public.scan_reports(generated_by);

-- Report Schedules Indexes
CREATE INDEX idx_report_schedules_project ON public.report_schedules(project_id);
CREATE INDEX idx_report_schedules_active ON public.report_schedules(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_report_schedules_next_run ON public.report_schedules(next_run_at) WHERE is_active = TRUE;

-- Dashboard Metrics Indexes
CREATE INDEX idx_dashboard_metrics_project ON public.dashboard_metrics(project_id);
CREATE INDEX idx_dashboard_metrics_type ON public.dashboard_metrics(metric_type);
CREATE INDEX idx_dashboard_metrics_time ON public.dashboard_metrics(recorded_at);

-- Report Templates Indexes
CREATE INDEX idx_report_templates_type ON public.report_templates(template_type);
CREATE INDEX idx_report_templates_default ON public.report_templates(is_default) WHERE is_default = TRUE;
CREATE INDEX idx_report_templates_public ON public.report_templates(is_public) WHERE is_public = TRUE;

-- Analytics Events Indexes
CREATE INDEX idx_analytics_events_occurred_at ON public.analytics_events(occurred_at);
CREATE INDEX idx_analytics_events_type ON public.analytics_events(event_type);
CREATE INDEX idx_analytics_events_user ON public.analytics_events(user_id);
CREATE INDEX idx_analytics_events_project ON public.analytics_events(project_id);

-- Performance Metrics Indexes
CREATE INDEX idx_performance_metrics_time ON public.performance_metrics(recorded_at);
CREATE INDEX idx_performance_metrics_category ON public.performance_metrics(metric_category);

-- Export Jobs Indexes
CREATE INDEX idx_export_jobs_user ON public.export_jobs(user_id);
CREATE INDEX idx_export_jobs_project ON public.export_jobs(project_id);
CREATE INDEX idx_export_jobs_status ON public.export_jobs(status);
CREATE INDEX idx_export_jobs_created_at ON public.export_jobs(created_at);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Scan Reports
CREATE TRIGGER update_scan_reports_updated_at
    BEFORE UPDATE ON public.scan_reports
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Report Schedules
CREATE TRIGGER update_report_schedules_updated_at
    BEFORE UPDATE ON public.report_schedules
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Report Templates
CREATE TRIGGER update_report_templates_updated_at
    BEFORE UPDATE ON public.report_templates
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Export Jobs
CREATE TRIGGER update_export_jobs_updated_at
    BEFORE UPDATE ON public.export_jobs
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- FUNCTIONS AND PROCEDURES
-- =====================================================

-- Function to calculate next scheduled run time
CREATE OR REPLACE FUNCTION public.calculate_next_run_time(
    cron_expression TEXT,
    from_time TIMESTAMPTZ DEFAULT NOW()
) RETURNS TIMESTAMPTZ AS $$
DECLARE
    next_run TIMESTAMPTZ;
BEGIN
    -- Simple cron parser for common patterns
    -- This is a simplified version - in production, use a proper cron library
    CASE 
        WHEN cron_expression = '0 0 * * *' THEN -- Daily at midnight
            next_run := date_trunc('day', from_time) + INTERVAL '1 day';
        WHEN cron_expression = '0 0 * * 0' THEN -- Weekly on Sunday
            next_run := date_trunc('week', from_time) + INTERVAL '1 week';
        WHEN cron_expression = '0 0 1 * *' THEN -- Monthly on 1st
            next_run := date_trunc('month', from_time) + INTERVAL '1 month';
        WHEN cron_expression LIKE '0 % * * *' THEN -- Hourly at specific minute
            next_run := date_trunc('hour', from_time) + INTERVAL '1 hour';
        ELSE
            -- Default to daily if pattern not recognized
            next_run := date_trunc('day', from_time) + INTERVAL '1 day';
    END CASE;
    
    RETURN next_run;
END;
$$ LANGUAGE plpgsql;

-- Function to update report schedule next run time
CREATE OR REPLACE FUNCTION public.update_schedule_next_run()
RETURNS TRIGGER AS $$
BEGIN
    NEW.next_run_at := public.calculate_next_run_time(NEW.schedule_cron, COALESCE(NEW.last_run_at, NOW()));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update next_run_at
CREATE TRIGGER update_report_schedule_next_run
    BEFORE INSERT OR UPDATE ON public.report_schedules
    FOR EACH ROW
    EXECUTE FUNCTION public.update_schedule_next_run();

-- Function to record dashboard metric
CREATE OR REPLACE FUNCTION public.record_dashboard_metric(
    p_project_id UUID,
    p_metric_type VARCHAR(50),
    p_metric_name VARCHAR(100),
    p_metric_value NUMERIC,
    p_metric_unit VARCHAR(20) DEFAULT NULL,
    p_time_period VARCHAR(20) DEFAULT 'current',
    p_metadata JSONB DEFAULT '{}'::jsonb
) RETURNS UUID AS $$
DECLARE
    metric_id UUID;
BEGIN
    INSERT INTO public.dashboard_metrics (
        project_id, metric_type, metric_name, metric_value,
        metric_unit, time_period, metadata
    ) VALUES (
        p_project_id, p_metric_type, p_metric_name, p_metric_value,
        p_metric_unit, p_time_period, p_metadata
    ) RETURNING id INTO metric_id;
    
    RETURN metric_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- =====================================================

-- Project Analytics Summary
CREATE MATERIALIZED VIEW public.project_analytics_summary AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    COUNT(DISTINCT ss.id) as total_scans,
    COUNT(DISTINCT ss.id) FILTER (WHERE ss.status = 'completed') as completed_scans,
    COUNT(DISTINCT v.id) as total_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'critical') as critical_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'high') as high_vulnerabilities,
    COUNT(DISTINCT du.id) as total_urls_discovered,
    AVG(EXTRACT(EPOCH FROM (ss.completed_at - ss.started_at))) as avg_scan_duration_seconds,
    MAX(ss.created_at) as last_scan_date,
    COUNT(DISTINCT sr.id) as total_reports_generated
FROM public.projects p
LEFT JOIN public.scan_sessions ss ON p.id = ss.project_id
LEFT JOIN public.vulnerabilities v ON ss.id = v.session_id
LEFT JOIN public.discovered_urls du ON ss.id = du.session_id
LEFT JOIN public.scan_reports sr ON ss.id = sr.session_id
GROUP BY p.id, p.name;

-- Create unique index for materialized view refresh
CREATE UNIQUE INDEX idx_project_analytics_summary_project_id 
ON public.project_analytics_summary(project_id);

-- Vulnerability Trends Summary
CREATE MATERIALIZED VIEW public.vulnerability_trends_summary AS
SELECT 
    date_trunc('day', v.created_at) as trend_date,
    v.severity,
    vt.category,
    COUNT(*) as vulnerability_count,
    COUNT(DISTINCT v.session_id) as affected_scans,
    COUNT(DISTINCT ss.project_id) as affected_projects
FROM public.vulnerabilities v
JOIN public.scan_sessions ss ON v.session_id = ss.id
LEFT JOIN public.vulnerability_types vt ON v.vulnerability_type_id = vt.id
WHERE v.created_at >= NOW() - INTERVAL '90 days'
GROUP BY date_trunc('day', v.created_at), v.severity, vt.category
ORDER BY trend_date DESC, v.severity, vt.category;

-- Create unique index for vulnerability trends
CREATE UNIQUE INDEX idx_vulnerability_trends_summary_unique
ON public.vulnerability_trends_summary(trend_date, severity, category);

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION public.refresh_analytics_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.project_analytics_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.vulnerability_trends_summary;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default report templates
INSERT INTO public.report_templates (name, description, template_type, template_content, is_default, is_public) VALUES
('Executive Summary', 'High-level security overview for executives', 'pdf', '{"sections": ["summary", "risk_overview", "recommendations"], "charts": ["risk_distribution", "trend_analysis"]}', TRUE, TRUE),
('Technical Report', 'Detailed technical findings for security teams', 'pdf', '{"sections": ["executive_summary", "methodology", "findings", "technical_details", "remediation"], "include_raw_data": true}', TRUE, TRUE),
('Compliance Report', 'Compliance-focused report for auditors', 'pdf', '{"sections": ["compliance_summary", "findings_by_standard", "remediation_timeline"], "standards": ["owasp", "nist", "iso27001"]}', TRUE, TRUE),
('CSV Export', 'Raw data export in CSV format', 'csv', '{"columns": ["url", "vulnerability_type", "severity", "description", "remediation"], "include_metadata": false}', TRUE, TRUE),
('JSON Export', 'Machine-readable JSON export', 'json', '{"format": "structured", "include_metadata": true, "nested_objects": true}', TRUE, TRUE);

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.scan_reports IS 'Generated reports for scan sessions with file storage references';
COMMENT ON TABLE public.report_schedules IS 'Automated report generation schedules with cron expressions';
COMMENT ON TABLE public.dashboard_metrics IS 'Real-time metrics for dashboard widgets and analytics';
COMMENT ON TABLE public.report_templates IS 'Customizable report templates for different output formats';
COMMENT ON TABLE public.analytics_events IS 'User actions and system events for analytics and auditing';
COMMENT ON TABLE public.performance_metrics IS 'System performance and resource usage metrics';
COMMENT ON TABLE public.export_jobs IS 'Data export operations with status tracking';

COMMENT ON MATERIALIZED VIEW public.project_analytics_summary IS 'Aggregated analytics data per project for dashboard display';
COMMENT ON MATERIALIZED VIEW public.vulnerability_trends_summary IS 'Vulnerability trends over time for analytics charts';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify tables were created
SELECT 
    schemaname, 
    tablename, 
    tableowner 
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'scan_reports', 'report_schedules', 'dashboard_metrics',
        'report_templates', 'analytics_events', 'performance_metrics',
        'export_jobs'
    )
ORDER BY tablename;

-- Verify materialized views
SELECT 
    schemaname, 
    matviewname, 
    matviewowner 
FROM pg_matviews 
WHERE schemaname = 'public'
ORDER BY matviewname;

-- Verify functions
SELECT 
    routine_name, 
    routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
    AND routine_name IN (
        'calculate_next_run_time', 'update_schedule_next_run',
        'record_dashboard_metric', 'refresh_analytics_views'
    )
ORDER BY routine_name;