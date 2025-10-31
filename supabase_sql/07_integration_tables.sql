-- =====================================================
-- 07_integration_tables.sql
-- Notifications, Webhooks, and External Integrations
-- =====================================================

-- Notifications Table
-- User notifications and alerts
CREATE TABLE public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    notification_type public.notification_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error', 'success')),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    action_url TEXT, -- URL to navigate when notification is clicked
    metadata JSONB DEFAULT '{}'::jsonb,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integrations Table
-- External service integrations (Slack, Teams, JIRA, etc.)
CREATE TABLE public.integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    integration_type public.integration_type NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL, -- Service-specific config (encrypted sensitive data)
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    last_error_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure unique integration per project/type combination
    UNIQUE(project_id, integration_type, name)
);

-- Webhooks Table
-- Webhook endpoints for real-time notifications
CREATE TABLE public.webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    secret_key VARCHAR(255), -- For webhook signature verification
    events TEXT[] NOT NULL DEFAULT '{}', -- Array of event types to trigger webhook
    is_active BOOLEAN DEFAULT TRUE,
    retry_count INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    last_triggered_at TIMESTAMPTZ,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_error TEXT,
    last_error_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Webhook Deliveries Table
-- Track webhook delivery attempts and responses
CREATE TABLE public.webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID NOT NULL REFERENCES public.webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    response_headers JSONB,
    delivery_duration_ms INTEGER,
    attempt_number INTEGER DEFAULT 1,
    is_successful BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    delivered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Email Templates Table
-- Customizable email notification templates
CREATE TABLE public.email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    subject VARCHAR(200) NOT NULL,
    html_content TEXT NOT NULL,
    text_content TEXT,
    template_variables JSONB DEFAULT '[]'::jsonb, -- Available variables for substitution
    is_system_template BOOLEAN DEFAULT FALSE, -- System vs user-created templates
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notification Preferences Table
-- User preferences for different types of notifications
CREATE TABLE public.notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE, -- NULL for global preferences
    notification_type public.notification_type NOT NULL,
    email_enabled BOOLEAN DEFAULT TRUE,
    push_enabled BOOLEAN DEFAULT TRUE,
    webhook_enabled BOOLEAN DEFAULT FALSE,
    frequency VARCHAR(20) DEFAULT 'immediate' CHECK (frequency IN ('immediate', 'hourly', 'daily', 'weekly', 'disabled')),
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint for user/project/type combination
    UNIQUE(user_id, project_id, notification_type)
);

-- API Rate Limits Table
-- Track API usage and enforce rate limits
CREATE TABLE public.api_rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES public.api_keys(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMPTZ NOT NULL,
    window_duration_minutes INTEGER DEFAULT 60,
    limit_per_window INTEGER DEFAULT 1000,
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one record per user/endpoint/window
    UNIQUE(user_id, api_key_id, endpoint, window_start)
);

-- External API Credentials Table
-- Store encrypted credentials for external services
CREATE TABLE public.external_api_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID NOT NULL REFERENCES public.integrations(id) ON DELETE CASCADE,
    credential_type VARCHAR(50) NOT NULL, -- 'api_key', 'oauth_token', 'basic_auth'
    encrypted_credentials BYTEA NOT NULL, -- Encrypted credential data
    encryption_key_id VARCHAR(100), -- Reference to encryption key
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    last_validated_at TIMESTAMPTZ,
    validation_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integration Logs Table
-- Audit log for integration activities
CREATE TABLE public.integration_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES public.integrations(id) ON DELETE CASCADE,
    webhook_id UUID REFERENCES public.webhooks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- 'created', 'updated', 'triggered', 'failed'
    details TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CONSTRAINTS AND INDEXES
-- =====================================================

-- Notifications Indexes
CREATE INDEX idx_notifications_user ON public.notifications(user_id);
CREATE INDEX idx_notifications_project ON public.notifications(project_id);
CREATE INDEX idx_notifications_type ON public.notifications(notification_type);
CREATE INDEX idx_notifications_unread ON public.notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_created_at ON public.notifications(created_at);

-- Integrations Indexes
CREATE INDEX idx_integrations_project ON public.integrations(project_id);
CREATE INDEX idx_integrations_user ON public.integrations(user_id);
CREATE INDEX idx_integrations_type ON public.integrations(integration_type);
CREATE INDEX idx_integrations_active ON public.integrations(is_active) WHERE is_active = TRUE;

-- Webhooks Indexes
CREATE INDEX idx_webhooks_project ON public.webhooks(project_id);
CREATE INDEX idx_webhooks_user ON public.webhooks(user_id);
CREATE INDEX idx_webhooks_active ON public.webhooks(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_webhooks_events ON public.webhooks USING GIN(events);

-- Notification Preferences Indexes
CREATE INDEX idx_notification_preferences_user ON public.notification_preferences(user_id);
CREATE INDEX idx_notification_preferences_project ON public.notification_preferences(project_id);

-- API Rate Limits Indexes
CREATE INDEX idx_api_rate_limits_user ON public.api_rate_limits(user_id);
CREATE INDEX idx_api_rate_limits_api_key ON public.api_rate_limits(api_key_id);
CREATE INDEX idx_api_rate_limits_window ON public.api_rate_limits(window_start);
CREATE INDEX idx_api_rate_limits_blocked ON public.api_rate_limits(is_blocked) WHERE is_blocked = TRUE;

-- External API Credentials Indexes
CREATE INDEX idx_external_api_credentials_integration ON public.external_api_credentials(integration_id);
CREATE INDEX idx_external_api_credentials_active ON public.external_api_credentials(is_active) WHERE is_active = TRUE;

-- Webhook Deliveries Indexes
CREATE INDEX idx_webhook_deliveries_webhook_id ON public.webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_delivered_at ON public.webhook_deliveries(delivered_at);
CREATE INDEX idx_webhook_deliveries_success ON public.webhook_deliveries(is_successful);

-- Integration Logs Indexes
CREATE INDEX idx_integration_logs_integration ON public.integration_logs(integration_id);
CREATE INDEX idx_integration_logs_webhook ON public.integration_logs(webhook_id);
CREATE INDEX idx_integration_logs_occurred_at ON public.integration_logs(occurred_at);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Notifications
CREATE TRIGGER update_notifications_updated_at
    BEFORE UPDATE ON public.notifications
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Integrations
CREATE TRIGGER update_integrations_updated_at
    BEFORE UPDATE ON public.integrations
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Webhooks
CREATE TRIGGER update_webhooks_updated_at
    BEFORE UPDATE ON public.webhooks
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Email Templates
CREATE TRIGGER update_email_templates_updated_at
    BEFORE UPDATE ON public.email_templates
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Notification Preferences
CREATE TRIGGER update_notification_preferences_updated_at
    BEFORE UPDATE ON public.notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- API Rate Limits
CREATE TRIGGER update_api_rate_limits_updated_at
    BEFORE UPDATE ON public.api_rate_limits
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- External API Credentials
CREATE TRIGGER update_external_api_credentials_updated_at
    BEFORE UPDATE ON public.external_api_credentials
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- FUNCTIONS AND PROCEDURES
-- =====================================================

-- Function to create notification
CREATE OR REPLACE FUNCTION public.create_notification(
    p_user_id UUID,
    p_notification_type public.notification_type,
    p_title VARCHAR(200),
    p_message TEXT,
    p_project_id UUID DEFAULT NULL,
    p_session_id UUID DEFAULT NULL,
    p_severity VARCHAR(20) DEFAULT 'info',
    p_action_url TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'::jsonb,
    p_expires_at TIMESTAMPTZ DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    notification_id UUID;
BEGIN
    INSERT INTO public.notifications (
        user_id, project_id, session_id, notification_type,
        title, message, severity, action_url, metadata, expires_at
    ) VALUES (
        p_user_id, p_project_id, p_session_id, p_notification_type,
        p_title, p_message, p_severity, p_action_url, p_metadata, p_expires_at
    ) RETURNING id INTO notification_id;
    
    RETURN notification_id;
END;
$$ LANGUAGE plpgsql;

-- Function to mark notification as read
CREATE OR REPLACE FUNCTION public.mark_notification_read(
    p_notification_id UUID,
    p_user_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE public.notifications 
    SET is_read = TRUE, read_at = NOW(), updated_at = NOW()
    WHERE id = p_notification_id AND user_id = p_user_id AND is_read = FALSE;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Function to trigger webhook
CREATE OR REPLACE FUNCTION public.trigger_webhook(
    p_webhook_id UUID,
    p_event_type VARCHAR(50),
    p_payload JSONB
) RETURNS UUID AS $$
DECLARE
    delivery_id UUID;
    webhook_record RECORD;
BEGIN
    -- Get webhook details
    SELECT * INTO webhook_record 
    FROM public.webhooks 
    WHERE id = p_webhook_id AND is_active = TRUE;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Webhook not found or inactive: %', p_webhook_id;
    END IF;
    
    -- Check if event type is subscribed
    IF NOT (p_event_type = ANY(webhook_record.events)) THEN
        RAISE EXCEPTION 'Event type % not subscribed for webhook %', p_event_type, p_webhook_id;
    END IF;
    
    -- Create delivery record
    INSERT INTO public.webhook_deliveries (
        webhook_id, event_type, payload
    ) VALUES (
        p_webhook_id, p_event_type, p_payload
    ) RETURNING id INTO delivery_id;
    
    -- Update webhook last triggered time
    UPDATE public.webhooks 
    SET last_triggered_at = NOW(), updated_at = NOW()
    WHERE id = p_webhook_id;
    
    RETURN delivery_id;
END;
$$ LANGUAGE plpgsql;

-- Function to check API rate limit
CREATE OR REPLACE FUNCTION public.check_api_rate_limit(
    p_user_id UUID,
    p_api_key_id UUID,
    p_endpoint VARCHAR(100),
    p_limit_per_window INTEGER DEFAULT 1000,
    p_window_duration_minutes INTEGER DEFAULT 60
) RETURNS BOOLEAN AS $$
DECLARE
    current_window_start TIMESTAMPTZ;
    current_count INTEGER;
    rate_limit_record RECORD;
BEGIN
    -- Calculate current window start
    current_window_start := date_trunc('hour', NOW());
    
    -- Get or create rate limit record
    SELECT * INTO rate_limit_record
    FROM public.api_rate_limits
    WHERE user_id = p_user_id 
        AND COALESCE(api_key_id, p_api_key_id) = p_api_key_id
        AND endpoint = p_endpoint
        AND window_start = current_window_start;
    
    IF NOT FOUND THEN
        -- Create new rate limit record
        INSERT INTO public.api_rate_limits (
            user_id, api_key_id, endpoint, window_start,
            window_duration_minutes, limit_per_window, requests_count
        ) VALUES (
            p_user_id, p_api_key_id, p_endpoint, current_window_start,
            p_window_duration_minutes, p_limit_per_window, 1
        );
        RETURN TRUE;
    END IF;
    
    -- Check if blocked
    IF rate_limit_record.is_blocked AND rate_limit_record.blocked_until > NOW() THEN
        RETURN FALSE;
    END IF;
    
    -- Check if limit exceeded
    IF rate_limit_record.requests_count >= rate_limit_record.limit_per_window THEN
        -- Block for remainder of window
        UPDATE public.api_rate_limits
        SET is_blocked = TRUE,
            blocked_until = current_window_start + (p_window_duration_minutes || ' minutes')::INTERVAL,
            updated_at = NOW()
        WHERE id = rate_limit_record.id;
        RETURN FALSE;
    END IF;
    
    -- Increment request count
    UPDATE public.api_rate_limits
    SET requests_count = requests_count + 1,
        updated_at = NOW()
    WHERE id = rate_limit_record.id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default email templates
INSERT INTO public.email_templates (name, subject, html_content, text_content, template_variables, is_system_template) VALUES
('scan_completed', 'Scan Completed - {{project_name}}', 
 '<h2>Scan Completed</h2><p>Your scan for project <strong>{{project_name}}</strong> has completed successfully.</p><p>Found {{vulnerability_count}} vulnerabilities.</p><a href="{{scan_url}}">View Results</a>',
 'Scan Completed - {{project_name}}\n\nYour scan for project {{project_name}} has completed successfully.\nFound {{vulnerability_count}} vulnerabilities.\n\nView Results: {{scan_url}}',
 '["project_name", "vulnerability_count", "scan_url"]'::jsonb, TRUE),

('vulnerability_found', 'Critical Vulnerability Found - {{project_name}}', 
 '<h2>Critical Vulnerability Detected</h2><p>A {{severity}} vulnerability was found in project <strong>{{project_name}}</strong>.</p><p><strong>Type:</strong> {{vulnerability_type}}</p><p><strong>URL:</strong> {{url}}</p><a href="{{vulnerability_url}}">View Details</a>',
 'Critical Vulnerability Detected - {{project_name}}\n\nA {{severity}} vulnerability was found in project {{project_name}}.\nType: {{vulnerability_type}}\nURL: {{url}}\n\nView Details: {{vulnerability_url}}',
 '["project_name", "severity", "vulnerability_type", "url", "vulnerability_url"]'::jsonb, TRUE),

('scan_failed', 'Scan Failed - {{project_name}}', 
 '<h2>Scan Failed</h2><p>Your scan for project <strong>{{project_name}}</strong> has failed.</p><p><strong>Error:</strong> {{error_message}}</p><a href="{{project_url}}">View Project</a>',
 'Scan Failed - {{project_name}}\n\nYour scan for project {{project_name}} has failed.\nError: {{error_message}}\n\nView Project: {{project_url}}',
 '["project_name", "error_message", "project_url"]'::jsonb, TRUE),

('weekly_summary', 'Weekly Security Summary - {{project_name}}', 
 '<h2>Weekly Security Summary</h2><p>Here''s your weekly security summary for <strong>{{project_name}}</strong>:</p><ul><li>Scans completed: {{scans_completed}}</li><li>New vulnerabilities: {{new_vulnerabilities}}</li><li>Fixed vulnerabilities: {{fixed_vulnerabilities}}</li></ul><a href="{{dashboard_url}}">View Dashboard</a>',
 'Weekly Security Summary - {{project_name}}\n\nScans completed: {{scans_completed}}\nNew vulnerabilities: {{new_vulnerabilities}}\nFixed vulnerabilities: {{fixed_vulnerabilities}}\n\nView Dashboard: {{dashboard_url}}',
 '["project_name", "scans_completed", "new_vulnerabilities", "fixed_vulnerabilities", "dashboard_url"]'::jsonb, TRUE);

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.notifications IS 'User notifications and alerts for scan events and system updates';
COMMENT ON TABLE public.integrations IS 'External service integrations (Slack, Teams, JIRA, etc.)';
COMMENT ON TABLE public.webhooks IS 'Webhook endpoints for real-time event notifications';
COMMENT ON TABLE public.webhook_deliveries IS 'Webhook delivery attempts and response tracking';
COMMENT ON TABLE public.email_templates IS 'Customizable email notification templates';
COMMENT ON TABLE public.notification_preferences IS 'User preferences for different notification types and channels';
COMMENT ON TABLE public.api_rate_limits IS 'API usage tracking and rate limiting enforcement';
COMMENT ON TABLE public.external_api_credentials IS 'Encrypted credentials for external service integrations';
COMMENT ON TABLE public.integration_logs IS 'Audit log for integration activities and webhook triggers';

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
        'notifications', 'integrations', 'webhooks', 'webhook_deliveries',
        'email_templates', 'notification_preferences', 'api_rate_limits',
        'external_api_credentials', 'integration_logs'
    )
ORDER BY tablename;

-- Verify functions
SELECT 
    routine_name, 
    routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
    AND routine_name IN (
        'create_notification', 'mark_notification_read',
        'trigger_webhook', 'check_api_rate_limit'
    )
ORDER BY routine_name;

-- Check email templates
SELECT name, is_system_template, is_active FROM public.email_templates ORDER BY name;