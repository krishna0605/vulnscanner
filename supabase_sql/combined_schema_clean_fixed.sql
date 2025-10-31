-- =====================================================
-- ENHANCED VULNERABILITY SCANNER - COMPLETE SCHEMA (FIXED)
-- =====================================================
-- Combined schema file for Supabase PostgreSQL database
-- This file combines all schema components in proper execution order
-- 
-- FIXED VERSION: Replaces auth.users references with public.users
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

-- Users table (replaces auth.users)
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
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

-- User profiles table (extends users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
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
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
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
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
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
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
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
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
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
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- PART 3: PROJECT TABLES
-- =====================================================

-- Projects table
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
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
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',
    permissions JSONB DEFAULT '[]'::jsonb,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    invited_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    UNIQUE(project_id, user_id)
);

-- Scan configurations templates
CREATE TABLE public.scan_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

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
    created_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
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

-- =====================================================
-- TRIGGERS AND FUNCTIONS
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
    VALUES (NEW.id, NEW.email, NEW.full_name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Triggers for updated_at columns
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at
    BEFORE UPDATE ON public.api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_sessions_updated_at
    BEFORE UPDATE ON public.user_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scan_configurations_updated_at
    BEFORE UPDATE ON public.scan_configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scan_sessions_updated_at
    BEFORE UPDATE ON public.scan_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for new user registration
CREATE TRIGGER on_user_created
    AFTER INSERT ON public.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- =====================================================
-- INDEXES
-- =====================================================

-- Users table indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_username ON public.users(username);
CREATE INDEX idx_users_is_active ON public.users(is_active);

-- Projects table indexes
CREATE INDEX idx_projects_owner ON public.projects(owner_id);
CREATE INDEX idx_projects_domain ON public.projects(target_domain);
CREATE INDEX idx_projects_visibility ON public.projects(visibility);

-- Scan sessions indexes
CREATE INDEX idx_scan_sessions_project ON public.scan_sessions(project_id);
CREATE INDEX idx_scan_sessions_status ON public.scan_sessions(status);
CREATE INDEX idx_scan_sessions_created_by ON public.scan_sessions(created_by);

-- Discovered URLs indexes
CREATE INDEX idx_discovered_urls_session ON public.discovered_urls(session_id);
CREATE INDEX idx_discovered_urls_hash ON public.discovered_urls(url_hash);

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default system settings
INSERT INTO public.system_settings (key, value, description, is_public) VALUES
('max_concurrent_scans', '10', 'Maximum number of concurrent scans per user', true),
('default_scan_timeout', '3600', 'Default scan timeout in seconds', true),
('max_crawl_depth', '10', 'Maximum crawl depth allowed', true),
('rate_limit_requests_per_minute', '100', 'API rate limit per minute', true),
('maintenance_mode', 'false', 'System maintenance mode flag', true)
ON CONFLICT (key) DO NOTHING;

-- Create default admin user
INSERT INTO public.users (email, username, full_name, hashed_password, role, email_verified) VALUES
('admin@vulnscan.local', 'admin', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx/L/jG.', 'admin', true)
ON CONFLICT (email) DO NOTHING;