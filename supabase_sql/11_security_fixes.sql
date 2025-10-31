-- =====================================================
-- Security Fixes for Supabase Performance Security Lints
-- =====================================================
-- This file addresses all security issues identified in the CSV lint report
-- Run this after all other schema files have been executed
-- =====================================================

-- =====================================================
-- PART 1: ENABLE ROW LEVEL SECURITY ON MISSING TABLES
-- =====================================================

-- Enable RLS on core tables that are missing protection
ALTER TABLE public.extracted_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.technology_fingerprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_types ENABLE ROW LEVEL SECURITY;

-- Enable RLS on security analysis tables
ALTER TABLE public.ssl_certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.http_security_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dns_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_headers ENABLE ROW LEVEL SECURITY;

-- Enable RLS on integration and notification tables
ALTER TABLE public.webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_rate_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.external_api_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.integration_logs ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- PART 2: CREATE SECURE VIEWS (WITHOUT SECURITY DEFINER)
-- =====================================================

-- Project members with user details view
CREATE OR REPLACE VIEW project_members_with_users AS
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
JOIN public.profiles p ON pm.user_id = p.id
WHERE pm.project_id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
);

-- Technology summary view
CREATE OR REPLACE VIEW technology_summary AS
SELECT 
    tf.id,
    tf.url_id,
    tf.server_software,
    tf.programming_language,
    tf.framework,
    tf.cms,
    tf.javascript_libraries,
    tf.security_headers,
    tf.detected_at,
    du.url,
    ss.project_id
FROM public.technology_fingerprints tf
JOIN public.discovered_urls du ON tf.url_id = du.id
JOIN public.scan_sessions ss ON du.session_id = ss.id
WHERE ss.project_id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
);

-- Active scans view
CREATE OR REPLACE VIEW active_scans AS
SELECT 
    ss.id,
    ss.project_id,
    ss.status,
    ss.start_time,
    ss.configuration,
    ss.stats,
    p.name as project_name,
    p.target_domain
FROM public.scan_sessions ss
JOIN public.projects p ON ss.project_id = p.id
WHERE ss.status IN ('pending', 'queued', 'running', 'paused')
AND ss.project_id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
);

-- URL discovery summary view
CREATE OR REPLACE VIEW url_discovery_summary AS
SELECT 
    du.id,
    du.session_id,
    du.url,
    du.parent_url,
    du.method,
    du.status_code,
    du.content_type,
    du.content_length,
    du.response_time,
    du.page_title,
    du.discovered_at,
    ss.project_id
FROM public.discovered_urls du
JOIN public.scan_sessions ss ON du.session_id = ss.id
WHERE ss.project_id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
);

-- Vulnerability summary view (recreate without SECURITY DEFINER)
CREATE OR REPLACE VIEW vulnerability_summary AS
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
LEFT JOIN public.discovered_urls du ON v.url_id = du.id
WHERE ss.project_id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
);

-- Project overview view
CREATE OR REPLACE VIEW project_overview AS
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
    COUNT(DISTINCT ss.id) as total_scans,
    COUNT(DISTINCT v.id) as total_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'critical') as critical_vulnerabilities,
    COUNT(DISTINCT v.id) FILTER (WHERE v.severity = 'high') as high_vulnerabilities,
    MAX(ss.start_time) as last_scan_date
FROM public.projects p
LEFT JOIN public.scan_sessions ss ON p.id = ss.project_id
LEFT JOIN public.vulnerabilities v ON ss.id = v.session_id
WHERE p.id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
)
GROUP BY p.id, p.name, p.description, p.target_domain, p.owner_id, p.visibility, p.is_active, p.created_at, p.updated_at;

-- Security metrics view
CREATE OR REPLACE VIEW security_metrics AS
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
WHERE ss.project_id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
)
GROUP BY du.url, ss.project_id;

-- Recent vulnerabilities view
CREATE OR REPLACE VIEW recent_vulnerabilities AS
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
AND ss.project_id IN (
    SELECT id FROM public.projects 
    WHERE owner_id = auth.uid()
    UNION
    SELECT project_id FROM public.project_members 
    WHERE user_id = auth.uid()
)
ORDER BY v.created_at DESC;

-- =====================================================
-- PART 3: ROW LEVEL SECURITY POLICIES FOR NEW TABLES
-- =====================================================

-- Extracted forms policies
CREATE POLICY "Users can view forms from their project scans"
    ON public.extracted_forms FOR SELECT
    USING (url_id IN (
        SELECT du.id FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON du.session_id = ss.id
        WHERE ss.project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- Technology fingerprints policies
CREATE POLICY "Users can view technology fingerprints from their project scans"
    ON public.technology_fingerprints FOR SELECT
    USING (url_id IN (
        SELECT du.id FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON du.session_id = ss.id
        WHERE ss.project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- Vulnerabilities policies
CREATE POLICY "Users can view vulnerabilities from their project scans"
    ON public.vulnerabilities FOR SELECT
    USING (session_id IN (
        SELECT id FROM public.scan_sessions
        WHERE project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

CREATE POLICY "Users can update vulnerabilities from their project scans"
    ON public.vulnerabilities FOR UPDATE
    USING (session_id IN (
        SELECT id FROM public.scan_sessions
        WHERE project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- Vulnerability types policies (read-only for all authenticated users)
CREATE POLICY "Authenticated users can view vulnerability types"
    ON public.vulnerability_types FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- SSL certificates policies
CREATE POLICY "Users can view SSL certificates from their project scans"
    ON public.ssl_certificates FOR SELECT
    USING (url_id IN (
        SELECT du.id FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON du.session_id = ss.id
        WHERE ss.project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- HTTP security analysis policies
CREATE POLICY "Users can view HTTP security analysis from their project scans"
    ON public.http_security_analysis FOR SELECT
    USING (url_id IN (
        SELECT du.id FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON du.session_id = ss.id
        WHERE ss.project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- DNS records policies
CREATE POLICY "Users can view DNS records from their project scans"
    ON public.dns_records FOR SELECT
    USING (url_id IN (
        SELECT du.id FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON du.session_id = ss.id
        WHERE ss.project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- Security headers policies
CREATE POLICY "Users can view security headers from their project scans"
    ON public.security_headers FOR SELECT
    USING (url_id IN (
        SELECT du.id FROM public.discovered_urls du
        JOIN public.scan_sessions ss ON du.session_id = ss.id
        WHERE ss.project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- Webhook deliveries policies
CREATE POLICY "Users can view webhook deliveries for their project webhooks"
    ON public.webhook_deliveries FOR SELECT
    USING (webhook_id IN (
        SELECT id FROM public.webhooks
        WHERE project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- Email templates policies (admin only)
CREATE POLICY "Admins can manage email templates"
    ON public.email_templates FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = auth.uid() AND role = 'admin'
    ));

-- Notification preferences policies
CREATE POLICY "Users can manage their own notification preferences"
    ON public.notification_preferences FOR ALL
    USING (user_id = auth.uid());

-- API rate limits policies
CREATE POLICY "Users can view their own API rate limits"
    ON public.api_rate_limits FOR SELECT
    USING (user_id = auth.uid());

-- External API credentials policies
CREATE POLICY "Users can manage their own external API credentials"
    ON public.external_api_credentials FOR ALL
    USING (user_id = auth.uid());

-- Integration logs policies
CREATE POLICY "Users can view integration logs for their projects"
    ON public.integration_logs FOR SELECT
    USING (integration_id IN (
        SELECT id FROM public.integrations
        WHERE project_id IN (
            SELECT id FROM public.projects WHERE owner_id = auth.uid()
            UNION
            SELECT project_id FROM public.project_members WHERE user_id = auth.uid()
        )
    ));

-- =====================================================
-- PART 4: ADDITIONAL SECURITY ENHANCEMENTS
-- =====================================================

-- Create function to validate project access
CREATE OR REPLACE FUNCTION user_has_project_access(project_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.projects 
        WHERE id = project_uuid AND owner_id = auth.uid()
        UNION
        SELECT 1 FROM public.project_members 
        WHERE project_id = project_uuid AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if user is admin
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
-- PART 5: COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON VIEW project_members_with_users IS 'Project members with user profile information, filtered by user access';
COMMENT ON VIEW technology_summary IS 'Technology fingerprints summary for accessible projects';
COMMENT ON VIEW active_scans IS 'Currently active scan sessions for accessible projects';
COMMENT ON VIEW url_discovery_summary IS 'URL discovery results for accessible projects';
COMMENT ON VIEW vulnerability_summary IS 'Vulnerability summary for accessible projects';
COMMENT ON VIEW project_overview IS 'Project overview with statistics for accessible projects';
COMMENT ON VIEW security_metrics IS 'Security metrics and vulnerability counts by domain';
COMMENT ON VIEW recent_vulnerabilities IS 'Recently discovered vulnerabilities for accessible projects';

COMMENT ON FUNCTION user_has_project_access(UUID) IS 'Check if current user has access to specified project';
COMMENT ON FUNCTION user_is_admin() IS 'Check if current user has admin role';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment these to verify the fixes:

-- Check RLS is enabled on all tables
-- SELECT schemaname, tablename, rowsecurity 
-- FROM pg_tables 
-- WHERE schemaname = 'public' AND rowsecurity = false;

-- Check views are created without SECURITY DEFINER
-- SELECT viewname FROM pg_views WHERE schemaname = 'public';

-- Test view access
-- SELECT COUNT(*) FROM project_overview;
-- SELECT COUNT(*) FROM vulnerability_summary;

-- =====================================================
-- END OF SECURITY FIXES
-- =====================================================