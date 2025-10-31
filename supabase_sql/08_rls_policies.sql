-- =====================================================
-- 08_rls_policies.sql
-- Row Level Security (RLS) Policies for All Tables
-- =====================================================

-- =====================================================
-- ENABLE RLS ON ALL TABLES
-- =====================================================

-- Core Tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.usage_records ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.background_jobs ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY; -- Table not created yet

-- Project Tables
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_configurations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.project_invitations ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.project_comments ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.project_favorites ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.project_activity ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.project_statistics ENABLE ROW LEVEL SECURITY; -- Table not created yet

-- Scanning Tables
ALTER TABLE public.scan_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crawl_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.discovered_urls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.url_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.form_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.technology_fingerprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_headers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.crawl_metrics ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.crawl_errors ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.robots_policies ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.scheduled_scans ENABLE ROW LEVEL SECURITY; -- Table not created yet

-- Vulnerability Tables
ALTER TABLE public.vulnerability_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vulnerability_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ssl_certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dns_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.http_security_analysis ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.vulnerability_comments ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.vulnerability_assignments ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.vulnerability_remediations ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.vulnerability_trends ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.vulnerability_patterns ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.compliance_frameworks ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.vulnerability_compliance ENABLE ROW LEVEL SECURITY; -- Table not created yet

-- Reporting Tables
ALTER TABLE public.scan_reports ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.report_schedules ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.dashboard_metrics ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.report_templates ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY; -- Table not created yet
-- ALTER TABLE public.export_jobs ENABLE ROW LEVEL SECURITY; -- Table not created yet

-- Integration Tables
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
-- HELPER FUNCTIONS FOR RLS
-- =====================================================

-- Function to check if user is project member
CREATE OR REPLACE FUNCTION public.is_project_member(project_id UUID, user_id UUID DEFAULT auth.uid())
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.project_members pm
        WHERE pm.project_id = $1 AND pm.user_id = COALESCE($2, auth.uid())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is project owner
CREATE OR REPLACE FUNCTION public.is_project_owner(project_id UUID, user_id UUID DEFAULT auth.uid())
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.projects p
        WHERE p.id = $1 AND p.owner_id = COALESCE($2, auth.uid())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has project role
CREATE OR REPLACE FUNCTION public.has_project_role(project_id UUID, required_role TEXT, user_id UUID DEFAULT auth.uid())
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.project_members pm
        WHERE pm.project_id = $1 
            AND pm.user_id = COALESCE($3, auth.uid())
            AND pm.role::TEXT = $2
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION public.is_admin(user_id UUID DEFAULT auth.uid())
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles p
        WHERE p.id = COALESCE($1, auth.uid()) AND p.role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- CORE TABLE POLICIES
-- =====================================================

-- Profiles Policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles"
    ON public.profiles FOR SELECT
    USING (public.is_admin());

-- API Keys Policies
CREATE POLICY "Users can manage their own API keys"
    ON public.api_keys FOR ALL
    USING (auth.uid() = user_id);

-- User Sessions Policies
CREATE POLICY "Users can view their own sessions"
    ON public.user_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own sessions"
    ON public.user_sessions FOR UPDATE
    USING (auth.uid() = user_id);

-- Subscriptions Policies (Table not created yet)
-- CREATE POLICY "Users can view their own subscription"
--     ON public.subscriptions FOR SELECT
--     USING (auth.uid() = user_id);

-- CREATE POLICY "Admins can manage all subscriptions"
--     ON public.subscriptions FOR ALL
--     USING (public.is_admin());

-- Usage Records Policies (Table not created yet)
-- CREATE POLICY "Users can view their own usage records"
--     ON public.usage_records FOR SELECT
--     USING (auth.uid() = user_id);

-- CREATE POLICY "Admins can view all usage records"
--     ON public.usage_records FOR SELECT
--     USING (public.is_admin());

-- System Settings Policies (Admin only) (Table not created yet)
-- CREATE POLICY "Admins can manage system settings"
--     ON public.system_settings FOR ALL
--     USING (public.is_admin());

-- Background Jobs Policies (Table not created yet)
-- CREATE POLICY "Users can view their own background jobs"
--     ON public.background_jobs FOR SELECT
--     USING (auth.uid() = user_id);

-- CREATE POLICY "Admins can manage all background jobs"
--     ON public.background_jobs FOR ALL
--     USING (public.is_admin());

-- Activity Logs Policies (Table not created yet)
-- CREATE POLICY "Users can view their own activity logs"
--     ON public.activity_logs FOR SELECT
--     USING (auth.uid() = user_id);

-- CREATE POLICY "Admins can view all activity logs"
--     ON public.activity_logs FOR SELECT
--     USING (public.is_admin());

-- =====================================================
-- PROJECT TABLE POLICIES
-- =====================================================

-- Projects Policies
CREATE POLICY "Users can view projects they are members of"
    ON public.projects FOR SELECT
    USING (
        auth.uid() = owner_id OR 
        public.is_project_member(id) OR
        visibility = 'public'
    );

CREATE POLICY "Users can create projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Project owners can update their projects"
    ON public.projects FOR UPDATE
    USING (auth.uid() = owner_id);

CREATE POLICY "Project owners can delete their projects"
    ON public.projects FOR DELETE
    USING (auth.uid() = owner_id);

-- Project Members Policies
CREATE POLICY "Project members can view project membership"
    ON public.project_members FOR SELECT
    USING (public.is_project_member(project_id));

CREATE POLICY "Project owners can manage project members"
    ON public.project_members FOR ALL
    USING (public.is_project_owner(project_id));

-- Project Settings Policies
CREATE POLICY "Project members can view project settings"
    ON public.project_settings FOR SELECT
    USING (public.is_project_member(project_id));

CREATE POLICY "Project owners and admins can manage project settings"
    ON public.project_settings FOR ALL
    USING (
        public.is_project_owner(project_id) OR
        public.has_project_role(project_id, 'admin')
    );

-- Scan Configurations Policies
CREATE POLICY "Project members can view scan configurations"
    ON public.scan_configurations FOR SELECT
    USING (public.is_project_member(project_id));

CREATE POLICY "Project members with admin role can manage scan configurations"
    ON public.scan_configurations FOR ALL
    USING (
        public.is_project_owner(project_id) OR
        public.has_project_role(project_id, 'admin') OR
        public.has_project_role(project_id, 'editor')
    );

-- Project Invitations Policies
CREATE POLICY "Project owners can manage invitations"
    ON public.project_invitations FOR ALL
    USING (public.is_project_owner(project_id));

CREATE POLICY "Invited users can view their invitations"
    ON public.project_invitations FOR SELECT
    USING (auth.jwt() ->> 'email' = invited_email);

-- Project Comments Policies
CREATE POLICY "Project members can view comments"
    ON public.project_comments FOR SELECT
    USING (public.is_project_member(project_id));

CREATE POLICY "Project members can create comments"
    ON public.project_comments FOR INSERT
    WITH CHECK (
        public.is_project_member(project_id) AND
        auth.uid() = user_id
    );

CREATE POLICY "Users can update their own comments"
    ON public.project_comments FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own comments or project owners can delete any"
    ON public.project_comments FOR DELETE
    USING (
        auth.uid() = user_id OR
        public.is_project_owner(project_id)
    );

-- Project Favorites Policies
CREATE POLICY "Users can manage their own project favorites"
    ON public.project_favorites FOR ALL
    USING (auth.uid() = user_id);

-- Project Activity Policies
CREATE POLICY "Project members can view project activity"
    ON public.project_activity FOR SELECT
    USING (public.is_project_member(project_id));

-- Project Statistics Policies
CREATE POLICY "Project members can view project statistics"
    ON public.project_statistics FOR SELECT
    USING (public.is_project_member(project_id));

-- =====================================================
-- SCANNING TABLE POLICIES
-- =====================================================

-- Scan Sessions Policies
CREATE POLICY "Project members can view scan sessions"
    ON public.scan_sessions FOR SELECT
    USING (public.is_project_member(project_id));

CREATE POLICY "Project members can create scan sessions"
    ON public.scan_sessions FOR INSERT
    WITH CHECK (
        public.is_project_member(project_id) AND
        auth.uid() = created_by
    );

CREATE POLICY "Scan creators and project admins can update scan sessions"
    ON public.scan_sessions FOR UPDATE
    USING (
        auth.uid() = created_by OR
        public.is_project_owner(project_id) OR
        public.has_project_role(project_id, 'admin')
    );

-- Crawl Queue Policies
CREATE POLICY "Project members can view crawl queue for their project scans"
    ON public.crawl_queue FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- Discovered URLs Policies
CREATE POLICY "Project members can view discovered URLs for their project scans"
    ON public.discovered_urls FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- URL Metadata Policies
CREATE POLICY "Project members can view URL metadata for their project scans"
    ON public.url_metadata FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON du.session_id = ss.id
            WHERE du.id = url_id AND public.is_project_member(ss.project_id)
        )
    );

-- Extracted Forms Policies
CREATE POLICY "Project members can view extracted forms for their project scans"
    ON public.extracted_forms FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON du.session_id = ss.id
            WHERE du.id = url_id AND public.is_project_member(ss.project_id)
        )
    );

-- Form Fields Policies
CREATE POLICY "Project members can view form fields for their project scans"
    ON public.form_fields FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.extracted_forms ef
            JOIN public.discovered_urls du ON ef.url_id = du.id
            JOIN public.scan_sessions ss ON du.session_id = ss.id
            WHERE ef.id = form_id AND public.is_project_member(ss.project_id)
        )
    );

-- Technology Fingerprints Policies
CREATE POLICY "Project members can view technology fingerprints for their project scans"
    ON public.technology_fingerprints FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON du.session_id = ss.id
            WHERE du.id = url_id AND public.is_project_member(ss.project_id)
        )
    );

-- Security Headers Policies
CREATE POLICY "Project members can view security headers for their project scans"
    ON public.security_headers FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON du.session_id = ss.id
            WHERE du.id = url_id AND public.is_project_member(ss.project_id)
        )
    );

-- Crawl Metrics Policies
CREATE POLICY "Project members can view crawl metrics for their project scans"
    ON public.crawl_metrics FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- Crawl Errors Policies
CREATE POLICY "Project members can view crawl errors for their project scans"
    ON public.crawl_errors FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- Robots Policies Policies
CREATE POLICY "All authenticated users can view robots policies"
    ON public.robots_policies FOR SELECT
    USING (auth.role() = 'authenticated');

-- Scheduled Scans Policies
CREATE POLICY "Project members can view scheduled scans"
    ON public.scheduled_scans FOR SELECT
    USING (public.is_project_member(project_id));

CREATE POLICY "Project admins can manage scheduled scans"
    ON public.scheduled_scans FOR ALL
    USING (
        public.is_project_owner(project_id) OR
        public.has_project_role(project_id, 'admin') OR
        public.has_project_role(project_id, 'editor')
    );

-- =====================================================
-- VULNERABILITY TABLE POLICIES
-- =====================================================

-- Vulnerability Types Policies (Public read access)
CREATE POLICY "All authenticated users can view vulnerability types"
    ON public.vulnerability_types FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage vulnerability types"
    ON public.vulnerability_types FOR ALL
    USING (public.is_admin());

-- Vulnerabilities Policies
CREATE POLICY "Project members can view vulnerabilities for their project scans"
    ON public.vulnerabilities FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- Vulnerability Instances Policies
CREATE POLICY "Project members can view vulnerability instances for their project scans"
    ON public.vulnerability_instances FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND public.is_project_member(ss.project_id)
        )
    );

-- SSL Certificates Policies
CREATE POLICY "Project members can view SSL certificates for their project scans"
    ON public.ssl_certificates FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- DNS Records Policies
CREATE POLICY "Project members can view DNS records for their project scans"
    ON public.dns_records FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- HTTP Security Analysis Policies
CREATE POLICY "Project members can view HTTP security analysis for their project scans"
    ON public.http_security_analysis FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- Vulnerability Comments Policies
CREATE POLICY "Project members can view vulnerability comments"
    ON public.vulnerability_comments FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND public.is_project_member(ss.project_id)
        )
    );

CREATE POLICY "Project members can create vulnerability comments"
    ON public.vulnerability_comments FOR INSERT
    WITH CHECK (
        auth.uid() = user_id AND
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND public.is_project_member(ss.project_id)
        )
    );

CREATE POLICY "Users can update their own vulnerability comments"
    ON public.vulnerability_comments FOR UPDATE
    USING (auth.uid() = user_id);

-- Vulnerability Assignments Policies
CREATE POLICY "Project members can view vulnerability assignments"
    ON public.vulnerability_assignments FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND public.is_project_member(ss.project_id)
        )
    );

CREATE POLICY "Project admins can manage vulnerability assignments"
    ON public.vulnerability_assignments FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND (
                public.is_project_owner(ss.project_id) OR
                public.has_project_role(ss.project_id, 'admin')
            )
        )
    );

-- Vulnerability Remediations Policies
CREATE POLICY "Project members can view vulnerability remediations"
    ON public.vulnerability_remediations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND public.is_project_member(ss.project_id)
        )
    );

CREATE POLICY "Project members can create vulnerability remediations"
    ON public.vulnerability_remediations FOR INSERT
    WITH CHECK (
        auth.uid() = created_by AND
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND public.is_project_member(ss.project_id)
        )
    );

-- Vulnerability Trends Policies
CREATE POLICY "Project members can view vulnerability trends for their projects"
    ON public.vulnerability_trends FOR SELECT
    USING (public.is_project_member(project_id));

-- Vulnerability Patterns Policies (Admin only)
CREATE POLICY "Admins can manage vulnerability patterns"
    ON public.vulnerability_patterns FOR ALL
    USING (public.is_admin());

CREATE POLICY "All authenticated users can view vulnerability patterns"
    ON public.vulnerability_patterns FOR SELECT
    USING (auth.role() = 'authenticated');

-- Compliance Frameworks Policies (Public read access)
CREATE POLICY "All authenticated users can view compliance frameworks"
    ON public.compliance_frameworks FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage compliance frameworks"
    ON public.compliance_frameworks FOR ALL
    USING (public.is_admin());

-- Vulnerability Compliance Policies
CREATE POLICY "Project members can view vulnerability compliance for their project scans"
    ON public.vulnerability_compliance FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.vulnerabilities v
            JOIN public.scan_sessions ss ON v.session_id = ss.id
            WHERE v.id = vulnerability_id AND public.is_project_member(ss.project_id)
        )
    );

-- =====================================================
-- REPORTING TABLE POLICIES
-- =====================================================

-- Scan Reports Policies
CREATE POLICY "Project members can view scan reports for their project scans"
    ON public.scan_reports FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        ) OR is_public = TRUE
    );

CREATE POLICY "Users can create scan reports for scans they have access to"
    ON public.scan_reports FOR INSERT
    WITH CHECK (
        auth.uid() = generated_by AND
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            WHERE ss.id = session_id AND public.is_project_member(ss.project_id)
        )
    );

-- Report Schedules Policies
CREATE POLICY "Project members can view report schedules"
    ON public.report_schedules FOR SELECT
    USING (public.is_project_member(project_id));

CREATE POLICY "Project admins can manage report schedules"
    ON public.report_schedules FOR ALL
    USING (
        public.is_project_owner(project_id) OR
        public.has_project_role(project_id, 'admin')
    );

-- Dashboard Metrics Policies
CREATE POLICY "Project members can view dashboard metrics"
    ON public.dashboard_metrics FOR SELECT
    USING (
        project_id IS NULL OR
        public.is_project_member(project_id)
    );

-- Report Templates Policies
CREATE POLICY "All authenticated users can view public report templates"
    ON public.report_templates FOR SELECT
    USING (is_public = TRUE OR auth.uid() = created_by);

CREATE POLICY "Users can create their own report templates"
    ON public.report_templates FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update their own report templates"
    ON public.report_templates FOR UPDATE
    USING (auth.uid() = created_by);

CREATE POLICY "Admins can manage all report templates"
    ON public.report_templates FOR ALL
    USING (public.is_admin());

-- Analytics Events Policies
CREATE POLICY "Users can view their own analytics events"
    ON public.analytics_events FOR SELECT
    USING (
        auth.uid() = user_id OR
        (project_id IS NOT NULL AND public.is_project_member(project_id))
    );

CREATE POLICY "Admins can view all analytics events"
    ON public.analytics_events FOR SELECT
    USING (public.is_admin());

-- Performance Metrics Policies (Admin only)
CREATE POLICY "Admins can manage performance metrics"
    ON public.performance_metrics FOR ALL
    USING (public.is_admin());

-- Export Jobs Policies
CREATE POLICY "Users can view their own export jobs"
    ON public.export_jobs FOR SELECT
    USING (
        auth.uid() = user_id OR
        (project_id IS NOT NULL AND public.is_project_member(project_id))
    );

CREATE POLICY "Users can create export jobs for projects they have access to"
    ON public.export_jobs FOR INSERT
    WITH CHECK (
        auth.uid() = user_id AND
        (project_id IS NULL OR public.is_project_member(project_id))
    );

-- =====================================================
-- INTEGRATION TABLE POLICIES
-- =====================================================

-- Notifications Policies
CREATE POLICY "Users can view their own notifications"
    ON public.notifications FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own notifications"
    ON public.notifications FOR UPDATE
    USING (auth.uid() = user_id);

-- Integrations Policies
CREATE POLICY "Project members can view project integrations"
    ON public.integrations FOR SELECT
    USING (
        public.is_project_member(project_id) OR
        auth.uid() = user_id
    );

CREATE POLICY "Project admins can manage project integrations"
    ON public.integrations FOR ALL
    USING (
        public.is_project_owner(project_id) OR
        public.has_project_role(project_id, 'admin') OR
        auth.uid() = user_id
    );

-- Webhooks Policies
CREATE POLICY "Project members can view project webhooks"
    ON public.webhooks FOR SELECT
    USING (
        public.is_project_member(project_id) OR
        auth.uid() = user_id
    );

CREATE POLICY "Project admins can manage project webhooks"
    ON public.webhooks FOR ALL
    USING (
        public.is_project_owner(project_id) OR
        public.has_project_role(project_id, 'admin') OR
        auth.uid() = user_id
    );

-- Webhook Deliveries Policies
CREATE POLICY "Project members can view webhook deliveries for their project webhooks"
    ON public.webhook_deliveries FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.webhooks w
            WHERE w.id = webhook_id AND (
                public.is_project_member(w.project_id) OR
                auth.uid() = w.user_id
            )
        )
    );

-- Email Templates Policies
CREATE POLICY "All authenticated users can view system email templates"
    ON public.email_templates FOR SELECT
    USING (is_system_template = TRUE OR auth.uid() = created_by);

CREATE POLICY "Users can create their own email templates"
    ON public.email_templates FOR INSERT
    WITH CHECK (auth.uid() = created_by AND is_system_template = FALSE);

CREATE POLICY "Users can update their own email templates"
    ON public.email_templates FOR UPDATE
    USING (auth.uid() = created_by AND is_system_template = FALSE);

CREATE POLICY "Admins can manage all email templates"
    ON public.email_templates FOR ALL
    USING (public.is_admin());

-- Notification Preferences Policies
CREATE POLICY "Users can manage their own notification preferences"
    ON public.notification_preferences FOR ALL
    USING (auth.uid() = user_id);

-- API Rate Limits Policies
CREATE POLICY "Users can view their own API rate limits"
    ON public.api_rate_limits FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all API rate limits"
    ON public.api_rate_limits FOR SELECT
    USING (public.is_admin());

-- External API Credentials Policies
CREATE POLICY "Integration owners can manage their external API credentials"
    ON public.external_api_credentials FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.integrations i
            WHERE i.id = integration_id AND (
                public.is_project_owner(i.project_id) OR
                public.has_project_role(i.project_id, 'admin') OR
                auth.uid() = i.user_id
            )
        )
    );

-- Integration Logs Policies
CREATE POLICY "Project members can view integration logs for their projects"
    ON public.integration_logs FOR SELECT
    USING (
        (integration_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM public.integrations i
            WHERE i.id = integration_id AND public.is_project_member(i.project_id)
        )) OR
        (webhook_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM public.webhooks w
            WHERE w.id = webhook_id AND public.is_project_member(w.project_id)
        )) OR
        auth.uid() = user_id
    );

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check RLS is enabled on all tables
SELECT 
    schemaname, 
    tablename, 
    rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
    AND rowsecurity = TRUE
ORDER BY tablename;

-- Check policies exist
SELECT 
    schemaname, 
    tablename, 
    policyname, 
    cmd,
    qual
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Check helper functions exist
SELECT 
    routine_name, 
    routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
    AND routine_name IN (
        'is_project_member', 'is_project_owner', 
        'has_project_role', 'is_admin'
    )
ORDER BY routine_name;