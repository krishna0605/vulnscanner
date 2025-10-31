-- =====================================================
-- Enhanced Vulnerability Scanner - Supabase Schema
-- =====================================================
-- This script creates the complete database schema for the Enhanced Vulnerability Scanner
-- including all tables, indexes, constraints, and Row Level Security (RLS) policies.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- PROFILES TABLE
-- =====================================================
-- Profiles table to extend Supabase auth.users with additional metadata
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- PROJECTS TABLE
-- =====================================================
-- Projects table for organizing vulnerability scans
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    target_domain VARCHAR(255) NOT NULL,
    scope_rules JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on projects
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- SCAN SESSIONS TABLE
-- =====================================================
-- Scan sessions table for tracking vulnerability scan executions
CREATE TABLE IF NOT EXISTS public.scan_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    configuration JSONB NOT NULL,
    stats JSONB DEFAULT '{}'::jsonb,
    created_by UUID NOT NULL REFERENCES auth.users(id)
);

-- Enable RLS on scan_sessions
ALTER TABLE public.scan_sessions ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- DISCOVERED URLS TABLE
-- =====================================================
-- Discovered URLs table for storing crawled endpoints
CREATE TABLE IF NOT EXISTS public.discovered_urls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    url VARCHAR(2000) NOT NULL,
    parent_url VARCHAR(2000),
    method VARCHAR(10) DEFAULT 'GET' CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')),
    status_code INTEGER CHECK (status_code >= 100 AND status_code <= 599),
    content_type VARCHAR(100),
    content_length INTEGER CHECK (content_length >= 0),
    response_time INTEGER CHECK (response_time >= 0), -- milliseconds
    page_title VARCHAR(500),
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, url, method)
);

-- Enable RLS on discovered_urls
ALTER TABLE public.discovered_urls ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- EXTRACTED FORMS TABLE
-- =====================================================
-- Extracted forms table for storing discovered forms and their fields
CREATE TABLE IF NOT EXISTS public.extracted_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID NOT NULL REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    form_action VARCHAR(2000),
    form_method VARCHAR(10) CHECK (form_method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    form_fields JSONB NOT NULL,
    csrf_tokens JSONB DEFAULT '[]'::jsonb,
    authentication_required BOOLEAN DEFAULT FALSE
);

-- Enable RLS on extracted_forms
ALTER TABLE public.extracted_forms ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- TECHNOLOGY FINGERPRINTS TABLE
-- =====================================================
-- Technology fingerprints table for storing detected technologies
CREATE TABLE IF NOT EXISTS public.technology_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_id UUID NOT NULL REFERENCES public.discovered_urls(id) ON DELETE CASCADE,
    server_software VARCHAR(100),
    programming_language VARCHAR(50),
    framework VARCHAR(100),
    cms VARCHAR(100),
    javascript_libraries JSONB DEFAULT '[]'::jsonb,
    security_headers JSONB DEFAULT '{}'::jsonb,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on technology_fingerprints
ALTER TABLE public.technology_fingerprints ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- DASHBOARD METRICS TABLE
-- =====================================================
-- Dashboard metrics table for storing real-time dashboard data
CREATE TABLE IF NOT EXISTS public.dashboard_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_type VARCHAR(50) NOT NULL CHECK (metric_type IN ('counter', 'gauge', 'histogram')),
    labels JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE
);

-- Enable RLS on dashboard_metrics
ALTER TABLE public.dashboard_metrics ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- REALTIME UPDATES TABLE
-- =====================================================
-- Real-time updates table for storing WebSocket broadcast data
CREATE TABLE IF NOT EXISTS public.realtime_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id)
);

-- Enable RLS on realtime_updates
ALTER TABLE public.realtime_updates ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_owner ON public.projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON public.projects(created_at);

-- Scan sessions indexes
CREATE INDEX IF NOT EXISTS idx_scan_sessions_project ON public.scan_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_status ON public.scan_sessions(status);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_created_by ON public.scan_sessions(created_by);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_start_time ON public.scan_sessions(start_time);

-- Discovered URLs indexes
CREATE INDEX IF NOT EXISTS idx_discovered_urls_session ON public.discovered_urls(session_id);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_parent ON public.discovered_urls(parent_url);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_status_code ON public.discovered_urls(status_code);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_discovered_at ON public.discovered_urls(discovered_at);

-- Extracted forms indexes
CREATE INDEX IF NOT EXISTS idx_extracted_forms_url ON public.extracted_forms(url_id);
CREATE INDEX IF NOT EXISTS idx_extracted_forms_method ON public.extracted_forms(form_method);

-- Technology fingerprints indexes
CREATE INDEX IF NOT EXISTS idx_tech_fingerprints_url ON public.technology_fingerprints(url_id);
CREATE INDEX IF NOT EXISTS idx_tech_fingerprints_detected_at ON public.technology_fingerprints(detected_at);

-- Dashboard metrics indexes
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_name_timestamp ON public.dashboard_metrics(metric_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_session ON public.dashboard_metrics(session_id);

-- Realtime updates indexes
CREATE INDEX IF NOT EXISTS idx_realtime_updates_event_type ON public.realtime_updates(event_type);
CREATE INDEX IF NOT EXISTS idx_realtime_updates_timestamp ON public.realtime_updates(timestamp);
CREATE INDEX IF NOT EXISTS idx_realtime_updates_user ON public.realtime_updates(user_id);
CREATE INDEX IF NOT EXISTS idx_realtime_updates_session ON public.realtime_updates(session_id);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Profiles policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Projects policies
CREATE POLICY "Users can view their own projects"
    ON public.projects FOR SELECT
    USING (auth.uid() = owner_id);

CREATE POLICY "Users can create their own projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Users can update their own projects"
    ON public.projects FOR UPDATE
    USING (auth.uid() = owner_id);

CREATE POLICY "Users can delete their own projects"
    ON public.projects FOR DELETE
    USING (auth.uid() = owner_id);

-- Scan sessions policies
CREATE POLICY "Users can view scan sessions for their projects"
    ON public.scan_sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.id = scan_sessions.project_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can create scan sessions for their projects"
    ON public.scan_sessions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.id = scan_sessions.project_id
            AND p.owner_id = auth.uid()
        )
        AND auth.uid() = created_by
    );

CREATE POLICY "Users can update scan sessions for their projects"
    ON public.scan_sessions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.id = scan_sessions.project_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete scan sessions for their projects"
    ON public.scan_sessions FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.projects p
            WHERE p.id = scan_sessions.project_id
            AND p.owner_id = auth.uid()
        )
    );

-- Discovered URLs policies
CREATE POLICY "Users can view discovered URLs for their scan sessions"
    ON public.discovered_urls FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = discovered_urls.session_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can create discovered URLs for their scan sessions"
    ON public.discovered_urls FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = discovered_urls.session_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can update discovered URLs for their scan sessions"
    ON public.discovered_urls FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = discovered_urls.session_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete discovered URLs for their scan sessions"
    ON public.discovered_urls FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = discovered_urls.session_id
            AND p.owner_id = auth.uid()
        )
    );

-- Extracted forms policies
CREATE POLICY "Users can view extracted forms for their discovered URLs"
    ON public.extracted_forms FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = extracted_forms.url_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can create extracted forms for their discovered URLs"
    ON public.extracted_forms FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = extracted_forms.url_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can update extracted forms for their discovered URLs"
    ON public.extracted_forms FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = extracted_forms.url_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete extracted forms for their discovered URLs"
    ON public.extracted_forms FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = extracted_forms.url_id
            AND p.owner_id = auth.uid()
        )
    );

-- Technology fingerprints policies
CREATE POLICY "Users can view technology fingerprints for their discovered URLs"
    ON public.technology_fingerprints FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = technology_fingerprints.url_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can create technology fingerprints for their discovered URLs"
    ON public.technology_fingerprints FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = technology_fingerprints.url_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can update technology fingerprints for their discovered URLs"
    ON public.technology_fingerprints FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = technology_fingerprints.url_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete technology fingerprints for their discovered URLs"
    ON public.technology_fingerprints FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls du
            JOIN public.scan_sessions ss ON ss.id = du.session_id
            JOIN public.projects p ON p.id = ss.project_id
            WHERE du.id = technology_fingerprints.url_id
            AND p.owner_id = auth.uid()
        )
    );

-- Dashboard metrics policies
CREATE POLICY "Users can view dashboard metrics for their scan sessions"
    ON public.dashboard_metrics FOR SELECT
    USING (
        session_id IS NULL OR
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = dashboard_metrics.session_id
            AND p.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can create dashboard metrics for their scan sessions"
    ON public.dashboard_metrics FOR INSERT
    WITH CHECK (
        session_id IS NULL OR
        EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = dashboard_metrics.session_id
            AND p.owner_id = auth.uid()
        )
    );

-- Realtime updates policies
CREATE POLICY "Users can view realtime updates for their data"
    ON public.realtime_updates FOR SELECT
    USING (
        user_id = auth.uid() OR
        (session_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = realtime_updates.session_id
            AND p.owner_id = auth.uid()
        ))
    );

CREATE POLICY "Users can create realtime updates for their data"
    ON public.realtime_updates FOR INSERT
    WITH CHECK (
        user_id = auth.uid() OR
        (session_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM public.scan_sessions ss
            JOIN public.projects p ON p.id = ss.project_id
            WHERE ss.id = realtime_updates.session_id
            AND p.owner_id = auth.uid()
        ))
    );

-- =====================================================
-- TRIGGERS AND FUNCTIONS
-- =====================================================

-- Function to automatically create a profile when a user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call the function when a new user is created
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to automatically update updated_at timestamps
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- SAMPLE DATA (OPTIONAL - FOR TESTING)
-- =====================================================

-- Note: Sample data should only be inserted after authentication is set up
-- and a user is logged in, as the policies require auth.uid() to be present.

-- Example queries to test after user authentication:
/*
-- Create a test project (run when authenticated)
INSERT INTO public.projects (name, description, owner_id, target_domain)
VALUES ('Test Project', 'A test project for vulnerability scanning', auth.uid(), 'example.com');

-- Create a test scan session
INSERT INTO public.scan_sessions (project_id, configuration, created_by)
SELECT id, '{"max_depth": 3, "max_pages": 100}'::jsonb, auth.uid()
FROM public.projects
WHERE owner_id = auth.uid()
LIMIT 1;

-- Test discovered URL
INSERT INTO public.discovered_urls (session_id, url, status_code, content_type)
SELECT id, 'https://example.com/', 200, 'text/html'
FROM public.scan_sessions
WHERE created_by = auth.uid()
LIMIT 1;
*/

-- =====================================================
-- SCHEMA VALIDATION QUERIES
-- =====================================================

-- Verify all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'profiles', 'projects', 'scan_sessions', 'discovered_urls', 
    'extracted_forms', 'technology_fingerprints', 'dashboard_metrics', 'realtime_updates'
)
ORDER BY table_name;

-- Verify RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'profiles', 'projects', 'scan_sessions', 'discovered_urls', 
    'extracted_forms', 'technology_fingerprints', 'dashboard_metrics', 'realtime_updates'
);

-- Verify indexes exist
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN (
    'profiles', 'projects', 'scan_sessions', 'discovered_urls', 
    'extracted_forms', 'technology_fingerprints', 'dashboard_metrics', 'realtime_updates'
)
ORDER BY tablename, indexname;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Enhanced Vulnerability Scanner schema setup completed successfully!';
    RAISE NOTICE '📋 Tables created: profiles, projects, scan_sessions, discovered_urls, extracted_forms, technology_fingerprints, dashboard_metrics, realtime_updates';
    RAISE NOTICE '🔒 Row Level Security (RLS) enabled on all tables';
    RAISE NOTICE '📊 Performance indexes created';
    RAISE NOTICE '🔄 Triggers and functions set up';
    RAISE NOTICE '🚀 Ready for application deployment!';
END $$;