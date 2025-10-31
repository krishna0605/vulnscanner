-- =====================================================
-- 09_indexes.sql
-- Performance Indexes and Constraints
-- =====================================================

-- =====================================================
-- CORE TABLE INDEXES
-- =====================================================

-- Profiles indexes
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON public.profiles(created_at);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username) WHERE username IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_profiles_email_search ON public.profiles USING gin(to_tsvector('english', COALESCE(full_name, '') || ' ' || COALESCE(username, '')));

-- API Keys indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON public.api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_is_active ON public.api_keys(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_api_keys_expires_at ON public.api_keys(expires_at) WHERE expires_at IS NOT NULL;

-- User Sessions indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON public.user_sessions(is_active) WHERE is_active = TRUE;

-- Subscriptions indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON public.subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_current_period_end ON public.subscriptions(current_period_end);

-- Usage Records indexes
CREATE INDEX IF NOT EXISTS idx_usage_records_user_id ON public.usage_records(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_records_date ON public.usage_records(date);
CREATE INDEX IF NOT EXISTS idx_usage_records_user_date ON public.usage_records(user_id, date);

-- Background Jobs indexes
CREATE INDEX IF NOT EXISTS idx_background_jobs_user_id ON public.background_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_background_jobs_status ON public.background_jobs(status);
CREATE INDEX IF NOT EXISTS idx_background_jobs_job_type ON public.background_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_background_jobs_scheduled_at ON public.background_jobs(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_background_jobs_queue ON public.background_jobs(status, scheduled_at) WHERE status IN ('pending', 'running');

-- Activity Logs indexes
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON public.activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON public.activity_logs(action);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON public.activity_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_logs_resource_type ON public.activity_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_activity_logs_resource_id ON public.activity_logs(resource_id);

-- =====================================================
-- PROJECT TABLE INDEXES
-- =====================================================

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_owner_id ON public.projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_projects_visibility ON public.projects(visibility);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON public.projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON public.projects(updated_at);
CREATE INDEX IF NOT EXISTS idx_projects_target_domain ON public.projects(target_domain);
CREATE INDEX IF NOT EXISTS idx_projects_name_search ON public.projects USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Project Members indexes
CREATE INDEX IF NOT EXISTS idx_project_members_project_id ON public.project_members(project_id);
CREATE INDEX IF NOT EXISTS idx_project_members_user_id ON public.project_members(user_id);
CREATE INDEX IF NOT EXISTS idx_project_members_role ON public.project_members(role);
CREATE INDEX IF NOT EXISTS idx_project_members_project_user ON public.project_members(project_id, user_id);

-- Project Settings indexes
CREATE INDEX IF NOT EXISTS idx_project_settings_project_id ON public.project_settings(project_id);

-- Scan Configurations indexes
CREATE INDEX IF NOT EXISTS idx_scan_configurations_project_id ON public.scan_configurations(project_id);
CREATE INDEX IF NOT EXISTS idx_scan_configurations_name ON public.scan_configurations(name);
CREATE INDEX IF NOT EXISTS idx_scan_configurations_is_default ON public.scan_configurations(is_default) WHERE is_default = TRUE;

-- Project Invitations indexes
CREATE INDEX IF NOT EXISTS idx_project_invitations_project_id ON public.project_invitations(project_id);
CREATE INDEX IF NOT EXISTS idx_project_invitations_invited_email ON public.project_invitations(invited_email);
CREATE INDEX IF NOT EXISTS idx_project_invitations_token ON public.project_invitations(token);
CREATE INDEX IF NOT EXISTS idx_project_invitations_status ON public.project_invitations(status);
CREATE INDEX IF NOT EXISTS idx_project_invitations_expires_at ON public.project_invitations(expires_at);

-- Project Comments indexes
CREATE INDEX IF NOT EXISTS idx_project_comments_project_id ON public.project_comments(project_id);
CREATE INDEX IF NOT EXISTS idx_project_comments_user_id ON public.project_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_project_comments_created_at ON public.project_comments(created_at);

-- Project Favorites indexes
CREATE INDEX IF NOT EXISTS idx_project_favorites_user_id ON public.project_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_project_favorites_project_id ON public.project_favorites(project_id);

-- Project Activity indexes
CREATE INDEX IF NOT EXISTS idx_project_activity_project_id ON public.project_activity(project_id);
CREATE INDEX IF NOT EXISTS idx_project_activity_user_id ON public.project_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_project_activity_action ON public.project_activity(action);
CREATE INDEX IF NOT EXISTS idx_project_activity_created_at ON public.project_activity(created_at);

-- Project Statistics indexes
CREATE INDEX IF NOT EXISTS idx_project_statistics_project_id ON public.project_statistics(project_id);
CREATE INDEX IF NOT EXISTS idx_project_statistics_date ON public.project_statistics(date);

-- =====================================================
-- SCANNING TABLE INDEXES
-- =====================================================

-- Scan Sessions indexes
CREATE INDEX IF NOT EXISTS idx_scan_sessions_project_id ON public.scan_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_status ON public.scan_sessions(status);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_created_by ON public.scan_sessions(created_by);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_start_time ON public.scan_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_end_time ON public.scan_sessions(end_time);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_active ON public.scan_sessions(status, start_time) WHERE status IN ('pending', 'running');

-- Crawl Queue indexes
CREATE INDEX IF NOT EXISTS idx_crawl_queue_session_id ON public.crawl_queue(session_id);
CREATE INDEX IF NOT EXISTS idx_crawl_queue_status ON public.crawl_queue(status);
CREATE INDEX IF NOT EXISTS idx_crawl_queue_priority ON public.crawl_queue(priority);
CREATE INDEX IF NOT EXISTS idx_crawl_queue_scheduled_at ON public.crawl_queue(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_crawl_queue_processing ON public.crawl_queue(status, priority, scheduled_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_crawl_queue_url_hash ON public.crawl_queue(url_hash);

-- Discovered URLs indexes
CREATE INDEX IF NOT EXISTS idx_discovered_urls_session_id ON public.discovered_urls(session_id);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_parent_url_id ON public.discovered_urls(parent_url_id);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_status_code ON public.discovered_urls(status_code);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_content_type ON public.discovered_urls(content_type);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_discovered_at ON public.discovered_urls(discovered_at);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_url_hash ON public.discovered_urls(url_hash);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_domain ON public.discovered_urls(domain);

-- URL Metadata indexes
CREATE INDEX IF NOT EXISTS idx_url_metadata_url_id ON public.url_metadata(url_id);
CREATE INDEX IF NOT EXISTS idx_url_metadata_content_hash ON public.url_metadata(content_hash);

-- Extracted Forms indexes
CREATE INDEX IF NOT EXISTS idx_extracted_forms_url_id ON public.extracted_forms(url_id);
CREATE INDEX IF NOT EXISTS idx_extracted_forms_form_action_hash ON public.extracted_forms(form_action_hash);
CREATE INDEX IF NOT EXISTS idx_extracted_forms_method ON public.extracted_forms(method);

-- Form Fields indexes
CREATE INDEX IF NOT EXISTS idx_form_fields_form_id ON public.form_fields(form_id);
CREATE INDEX IF NOT EXISTS idx_form_fields_field_type ON public.form_fields(field_type);
CREATE INDEX IF NOT EXISTS idx_form_fields_is_required ON public.form_fields(is_required);

-- Technology Fingerprints indexes
CREATE INDEX IF NOT EXISTS idx_technology_fingerprints_url_id ON public.technology_fingerprints(url_id);
CREATE INDEX IF NOT EXISTS idx_technology_fingerprints_technology ON public.technology_fingerprints(technology);
CREATE INDEX IF NOT EXISTS idx_technology_fingerprints_category ON public.technology_fingerprints(category);
CREATE INDEX IF NOT EXISTS idx_technology_fingerprints_confidence ON public.technology_fingerprints(confidence);

-- Security Headers indexes
CREATE INDEX IF NOT EXISTS idx_security_headers_url_id ON public.security_headers(url_id);
CREATE INDEX IF NOT EXISTS idx_security_headers_header_name ON public.security_headers(header_name);

-- Crawl Metrics indexes
CREATE INDEX IF NOT EXISTS idx_crawl_metrics_session_id ON public.crawl_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_crawl_metrics_timestamp ON public.crawl_metrics(timestamp);

-- Crawl Errors indexes
CREATE INDEX IF NOT EXISTS idx_crawl_errors_session_id ON public.crawl_errors(session_id);
CREATE INDEX IF NOT EXISTS idx_crawl_errors_error_type ON public.crawl_errors(error_type);
CREATE INDEX IF NOT EXISTS idx_crawl_errors_occurred_at ON public.crawl_errors(occurred_at);

-- Robots Policies indexes
CREATE INDEX IF NOT EXISTS idx_robots_policies_domain ON public.robots_policies(domain);
CREATE INDEX IF NOT EXISTS idx_robots_policies_user_agent ON public.robots_policies(user_agent);

-- Scheduled Scans indexes
CREATE INDEX IF NOT EXISTS idx_scheduled_scans_project_id ON public.scheduled_scans(project_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_scans_is_active ON public.scheduled_scans(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_scheduled_scans_next_run ON public.scheduled_scans(next_run) WHERE is_active = TRUE;

-- =====================================================
-- VULNERABILITY TABLE INDEXES
-- =====================================================

-- Vulnerability Types indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_types_category ON public.vulnerability_types(category);
CREATE INDEX IF NOT EXISTS idx_vulnerability_types_severity ON public.vulnerability_types(severity);
CREATE INDEX IF NOT EXISTS idx_vulnerability_types_cwe_id ON public.vulnerability_types(cwe_id);

-- Vulnerabilities indexes
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_session_id ON public.vulnerabilities(session_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_type_id ON public.vulnerabilities(type_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON public.vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_status ON public.vulnerabilities(status);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_risk_score ON public.vulnerabilities(risk_score);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_discovered_at ON public.vulnerabilities(discovered_at);

-- Vulnerability Instances indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_instances_vulnerability_id ON public.vulnerability_instances(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_instances_url_id ON public.vulnerability_instances(url_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_instances_parameter ON public.vulnerability_instances(parameter);

-- SSL Certificates indexes
CREATE INDEX IF NOT EXISTS idx_ssl_certificates_session_id ON public.ssl_certificates(session_id);
CREATE INDEX IF NOT EXISTS idx_ssl_certificates_domain ON public.ssl_certificates(domain);
CREATE INDEX IF NOT EXISTS idx_ssl_certificates_expires_at ON public.ssl_certificates(expires_at);
CREATE INDEX IF NOT EXISTS idx_ssl_certificates_is_valid ON public.ssl_certificates(is_valid);

-- DNS Records indexes
CREATE INDEX IF NOT EXISTS idx_dns_records_session_id ON public.dns_records(session_id);
CREATE INDEX IF NOT EXISTS idx_dns_records_domain ON public.dns_records(domain);
CREATE INDEX IF NOT EXISTS idx_dns_records_record_type ON public.dns_records(record_type);

-- HTTP Security Analysis indexes
CREATE INDEX IF NOT EXISTS idx_http_security_analysis_session_id ON public.http_security_analysis(session_id);
CREATE INDEX IF NOT EXISTS idx_http_security_analysis_url_id ON public.http_security_analysis(url_id);
CREATE INDEX IF NOT EXISTS idx_http_security_analysis_security_score ON public.http_security_analysis(security_score);

-- Vulnerability Comments indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_comments_vulnerability_id ON public.vulnerability_comments(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_comments_user_id ON public.vulnerability_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_comments_created_at ON public.vulnerability_comments(created_at);

-- Vulnerability Assignments indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_assignments_vulnerability_id ON public.vulnerability_assignments(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_assignments_assigned_to ON public.vulnerability_assignments(assigned_to);
CREATE INDEX IF NOT EXISTS idx_vulnerability_assignments_assigned_by ON public.vulnerability_assignments(assigned_by);
CREATE INDEX IF NOT EXISTS idx_vulnerability_assignments_status ON public.vulnerability_assignments(status);

-- Vulnerability Remediations indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_remediations_vulnerability_id ON public.vulnerability_remediations(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_remediations_created_by ON public.vulnerability_remediations(created_by);
CREATE INDEX IF NOT EXISTS idx_vulnerability_remediations_status ON public.vulnerability_remediations(status);

-- Vulnerability Trends indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_trends_project_id ON public.vulnerability_trends(project_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_trends_date ON public.vulnerability_trends(date);
CREATE INDEX IF NOT EXISTS idx_vulnerability_trends_severity ON public.vulnerability_trends(severity);

-- Vulnerability Patterns indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_patterns_pattern_type ON public.vulnerability_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_vulnerability_patterns_severity ON public.vulnerability_patterns(severity);

-- Compliance Frameworks indexes
CREATE INDEX IF NOT EXISTS idx_compliance_frameworks_code ON public.compliance_frameworks(code);

-- Vulnerability Compliance indexes
CREATE INDEX IF NOT EXISTS idx_vulnerability_compliance_vulnerability_id ON public.vulnerability_compliance(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_compliance_framework_id ON public.vulnerability_compliance(framework_id);
CREATE INDEX IF NOT EXISTS idx_vulnerability_compliance_compliance_status ON public.vulnerability_compliance(compliance_status);

-- =====================================================
-- REPORTING TABLE INDEXES
-- =====================================================

-- Scan Reports indexes
CREATE INDEX IF NOT EXISTS idx_scan_reports_session_id ON public.scan_reports(session_id);
CREATE INDEX IF NOT EXISTS idx_scan_reports_generated_by ON public.scan_reports(generated_by);
CREATE INDEX IF NOT EXISTS idx_scan_reports_format ON public.scan_reports(format);
CREATE INDEX IF NOT EXISTS idx_scan_reports_generated_at ON public.scan_reports(generated_at);
CREATE INDEX IF NOT EXISTS idx_scan_reports_is_public ON public.scan_reports(is_public) WHERE is_public = TRUE;

-- Report Schedules indexes
CREATE INDEX IF NOT EXISTS idx_report_schedules_project_id ON public.report_schedules(project_id);
CREATE INDEX IF NOT EXISTS idx_report_schedules_is_active ON public.report_schedules(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_report_schedules_next_run ON public.report_schedules(next_run) WHERE is_active = TRUE;

-- Dashboard Metrics indexes
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_project_id ON public.dashboard_metrics(project_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_metric_name ON public.dashboard_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_date ON public.dashboard_metrics(date);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_project_date ON public.dashboard_metrics(project_id, date);

-- Report Templates indexes
CREATE INDEX IF NOT EXISTS idx_report_templates_created_by ON public.report_templates(created_by);
CREATE INDEX IF NOT EXISTS idx_report_templates_template_type ON public.report_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_report_templates_is_public ON public.report_templates(is_public) WHERE is_public = TRUE;

-- Analytics Events indexes
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON public.analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_project_id ON public.analytics_events(project_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type ON public.analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON public.analytics_events(timestamp);

-- Performance Metrics indexes
CREATE INDEX IF NOT EXISTS idx_performance_metrics_metric_name ON public.performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON public.performance_metrics(timestamp);

-- Export Jobs indexes
CREATE INDEX IF NOT EXISTS idx_export_jobs_user_id ON public.export_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_export_jobs_project_id ON public.export_jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_export_jobs_status ON public.export_jobs(status);
CREATE INDEX IF NOT EXISTS idx_export_jobs_created_at ON public.export_jobs(created_at);

-- =====================================================
-- INTEGRATION TABLE INDEXES
-- =====================================================

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON public.notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON public.notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON public.notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON public.notifications(user_id, is_read, created_at) WHERE is_read = FALSE;

-- Integrations indexes
CREATE INDEX IF NOT EXISTS idx_integrations_project_id ON public.integrations(project_id);
CREATE INDEX IF NOT EXISTS idx_integrations_user_id ON public.integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_integrations_type ON public.integrations(type);
CREATE INDEX IF NOT EXISTS idx_integrations_is_active ON public.integrations(is_active) WHERE is_active = TRUE;

-- Webhooks indexes
CREATE INDEX IF NOT EXISTS idx_webhooks_project_id ON public.webhooks(project_id);
CREATE INDEX IF NOT EXISTS idx_webhooks_user_id ON public.webhooks(user_id);
CREATE INDEX IF NOT EXISTS idx_webhooks_is_active ON public.webhooks(is_active) WHERE is_active = TRUE;

-- Webhook Deliveries indexes
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook_id ON public.webhook_deliveries(webhook_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status ON public.webhook_deliveries(status);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_attempted_at ON public.webhook_deliveries(attempted_at);

-- Email Templates indexes
CREATE INDEX IF NOT EXISTS idx_email_templates_template_type ON public.email_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_email_templates_is_system ON public.email_templates(is_system_template);
CREATE INDEX IF NOT EXISTS idx_email_templates_created_by ON public.email_templates(created_by);

-- Notification Preferences indexes
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user_id ON public.notification_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_notification_type ON public.notification_preferences(notification_type);

-- API Rate Limits indexes
CREATE INDEX IF NOT EXISTS idx_api_rate_limits_user_id ON public.api_rate_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_api_rate_limits_endpoint ON public.api_rate_limits(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_rate_limits_window_start ON public.api_rate_limits(window_start);

-- External API Credentials indexes
CREATE INDEX IF NOT EXISTS idx_external_api_credentials_integration_id ON public.external_api_credentials(integration_id);
CREATE INDEX IF NOT EXISTS idx_external_api_credentials_provider ON public.external_api_credentials(provider);

-- Integration Logs indexes
CREATE INDEX IF NOT EXISTS idx_integration_logs_integration_id ON public.integration_logs(integration_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_webhook_id ON public.integration_logs(webhook_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_user_id ON public.integration_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_log_level ON public.integration_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_integration_logs_timestamp ON public.integration_logs(timestamp);

-- =====================================================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- =====================================================

-- Project member access patterns
CREATE INDEX IF NOT EXISTS idx_project_member_access ON public.project_members(project_id, user_id, role);

-- Scan session analysis
CREATE INDEX IF NOT EXISTS idx_scan_session_analysis ON public.scan_sessions(project_id, status, start_time);

-- URL discovery patterns
CREATE INDEX IF NOT EXISTS idx_url_discovery_patterns ON public.discovered_urls(session_id, status_code, discovered_at);

-- Vulnerability analysis
CREATE INDEX IF NOT EXISTS idx_vulnerability_analysis ON public.vulnerabilities(session_id, severity, status, discovered_at);

-- Security metrics
CREATE INDEX IF NOT EXISTS idx_security_metrics ON public.vulnerability_instances(vulnerability_id, url_id);

-- Reporting patterns
CREATE INDEX IF NOT EXISTS idx_reporting_patterns ON public.scan_reports(session_id, format, generated_at);

-- Activity tracking
CREATE INDEX IF NOT EXISTS idx_activity_tracking ON public.activity_logs(user_id, action, created_at);

-- Notification management
CREATE INDEX IF NOT EXISTS idx_notification_management ON public.notifications(user_id, type, is_read, created_at);

-- =====================================================
-- PARTIAL INDEXES FOR PERFORMANCE
-- =====================================================

-- Active scans only
CREATE INDEX IF NOT EXISTS idx_active_scans_only ON public.scan_sessions(project_id, start_time) 
WHERE status IN ('pending', 'running');

-- Unresolved vulnerabilities only
CREATE INDEX IF NOT EXISTS idx_unresolved_vulnerabilities ON public.vulnerabilities(session_id, severity, discovered_at) 
WHERE status IN ('open', 'confirmed');

-- Recent activity only (last 30 days)
CREATE INDEX IF NOT EXISTS idx_recent_activity ON public.activity_logs(user_id, action, created_at) 
WHERE created_at > (NOW() - INTERVAL '30 days');

-- Active integrations only
CREATE INDEX IF NOT EXISTS idx_active_integrations ON public.integrations(project_id, type) 
WHERE is_active = TRUE;

-- Failed webhook deliveries for retry
CREATE INDEX IF NOT EXISTS idx_failed_webhook_deliveries ON public.webhook_deliveries(webhook_id, attempted_at) 
WHERE status = 'failed' AND retry_count < 3;

-- =====================================================
-- GIN INDEXES FOR JSONB COLUMNS
-- =====================================================

-- Project scope rules search
CREATE INDEX IF NOT EXISTS idx_projects_scope_rules_gin ON public.projects USING gin(scope_rules);

-- Scan configuration search
CREATE INDEX IF NOT EXISTS idx_scan_configurations_config_gin ON public.scan_configurations USING gin(configuration);

-- Scan session statistics search
CREATE INDEX IF NOT EXISTS idx_scan_sessions_stats_gin ON public.scan_sessions USING gin(statistics);

-- URL metadata search
CREATE INDEX IF NOT EXISTS idx_url_metadata_metadata_gin ON public.url_metadata USING gin(metadata);

-- Form fields search
CREATE INDEX IF NOT EXISTS idx_extracted_forms_fields_gin ON public.extracted_forms USING gin(fields);

-- Technology fingerprint details search
CREATE INDEX IF NOT EXISTS idx_technology_fingerprints_details_gin ON public.technology_fingerprints USING gin(details);

-- Vulnerability evidence search
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_evidence_gin ON public.vulnerabilities USING gin(evidence);

-- Integration configuration search
CREATE INDEX IF NOT EXISTS idx_integrations_config_gin ON public.integrations USING gin(configuration);

-- Webhook payload search
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_payload_gin ON public.webhook_deliveries USING gin(payload);

-- =====================================================
-- TEXT SEARCH INDEXES
-- =====================================================

-- Full-text search for projects
CREATE INDEX IF NOT EXISTS idx_projects_fts ON public.projects 
USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Full-text search for vulnerabilities
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_fts ON public.vulnerabilities 
USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Full-text search for scan reports
CREATE INDEX IF NOT EXISTS idx_scan_reports_fts ON public.scan_reports 
USING gin(to_tsvector('english', title || ' ' || COALESCE(summary, '')));

-- =====================================================
-- UNIQUE CONSTRAINTS
-- =====================================================

-- Ensure unique project membership
ALTER TABLE public.project_members 
ADD CONSTRAINT uq_project_members_project_user UNIQUE (project_id, user_id);

-- Ensure unique API key hashes
ALTER TABLE public.api_keys 
ADD CONSTRAINT uq_api_keys_key_hash UNIQUE (key_hash);

-- Ensure unique session tokens
ALTER TABLE public.user_sessions 
ADD CONSTRAINT uq_user_sessions_session_token UNIQUE (session_token);

-- Ensure unique URL per session
ALTER TABLE public.discovered_urls 
ADD CONSTRAINT uq_discovered_urls_session_url UNIQUE (session_id, url_hash);

-- Ensure unique crawl queue entries
ALTER TABLE public.crawl_queue 
ADD CONSTRAINT uq_crawl_queue_session_url UNIQUE (session_id, url_hash);

-- Ensure unique vulnerability instances
ALTER TABLE public.vulnerability_instances 
ADD CONSTRAINT uq_vulnerability_instances UNIQUE (vulnerability_id, url_id, parameter);

-- Ensure unique project favorites
ALTER TABLE public.project_favorites 
ADD CONSTRAINT uq_project_favorites_user_project UNIQUE (user_id, project_id);

-- Ensure unique notification preferences
ALTER TABLE public.notification_preferences 
ADD CONSTRAINT uq_notification_preferences UNIQUE (user_id, notification_type);

-- Ensure unique compliance mappings
ALTER TABLE public.vulnerability_compliance 
ADD CONSTRAINT uq_vulnerability_compliance UNIQUE (vulnerability_id, framework_id);

-- =====================================================
-- CHECK CONSTRAINTS
-- =====================================================

-- Ensure valid email format in profiles
ALTER TABLE public.profiles 
ADD CONSTRAINT chk_profiles_email_format 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Ensure positive risk scores
ALTER TABLE public.vulnerabilities 
ADD CONSTRAINT chk_vulnerabilities_risk_score 
CHECK (risk_score >= 0 AND risk_score <= 10);

-- Ensure valid confidence scores
ALTER TABLE public.technology_fingerprints 
ADD CONSTRAINT chk_technology_fingerprints_confidence 
CHECK (confidence >= 0 AND confidence <= 1);

-- Ensure valid security scores
ALTER TABLE public.http_security_analysis 
ADD CONSTRAINT chk_http_security_analysis_score 
CHECK (security_score >= 0 AND security_score <= 100);

-- Ensure valid retry counts
ALTER TABLE public.webhook_deliveries 
ADD CONSTRAINT chk_webhook_deliveries_retry_count 
CHECK (retry_count >= 0 AND retry_count <= 10);

-- Ensure valid request counts
ALTER TABLE public.api_rate_limits 
ADD CONSTRAINT chk_api_rate_limits_request_count 
CHECK (request_count >= 0);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check all indexes are created
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Check unique constraints
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'public' 
    AND tc.constraint_type = 'UNIQUE'
ORDER BY tc.table_name, tc.constraint_name;

-- Check check constraints
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc 
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public' 
    AND tc.constraint_type = 'CHECK'
ORDER BY tc.table_name, tc.constraint_name;

-- Index usage statistics (run after some usage)
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    idx_scan, 
    idx_tup_read, 
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Table size and index size analysis
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;