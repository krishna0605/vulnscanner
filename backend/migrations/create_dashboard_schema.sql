-- Enhanced Vulnerability Scanner Dashboard Schema
-- This script creates the database schema for the dashboard functionality

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create profiles table for additional user data
-- (auth.users is managed by Supabase Auth)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create projects table
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    target_domain VARCHAR(255) NOT NULL,
    scope_rules JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create scan_sessions table
CREATE TABLE IF NOT EXISTS public.scan_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    stats JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES auth.users(id) NOT NULL
);

-- Create discovered_urls table
CREATE TABLE IF NOT EXISTS public.discovered_urls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES public.scan_sessions(id) ON DELETE CASCADE NOT NULL,
    url VARCHAR(2000) NOT NULL,
    parent_url VARCHAR(2000),
    method VARCHAR(10) DEFAULT 'GET',
    status_code INTEGER,
    content_type VARCHAR(100),
    content_length INTEGER,
    response_time INTEGER,
    page_title VARCHAR(500),
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, url, method)
);

-- Create extracted_forms table
CREATE TABLE IF NOT EXISTS public.extracted_forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE NOT NULL,
    form_action VARCHAR(2000),
    form_method VARCHAR(10),
    form_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    csrf_tokens JSONB DEFAULT '[]'::jsonb,
    authentication_required BOOLEAN DEFAULT FALSE
);

-- Create technology_fingerprints table
CREATE TABLE IF NOT EXISTS public.technology_fingerprints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url_id UUID REFERENCES public.discovered_urls(id) ON DELETE CASCADE NOT NULL,
    server_software VARCHAR(100),
    programming_language VARCHAR(50),
    framework VARCHAR(100),
    cms VARCHAR(100),
    javascript_libraries JSONB DEFAULT '[]'::jsonb,
    security_headers JSONB DEFAULT '{}'::jsonb,
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create dashboard_metrics table for storing custom metrics
CREATE TABLE IF NOT EXISTS public.dashboard_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    metric_data JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    INDEX(user_id, metric_name, timestamp)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON public.projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_projects_domain ON public.projects(target_domain);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_project ON public.scan_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_status ON public.scan_sessions(status);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_start_time ON public.scan_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_session ON public.discovered_urls(session_id);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_parent ON public.discovered_urls(parent_url);
CREATE INDEX IF NOT EXISTS idx_discovered_urls_status ON public.discovered_urls(status_code);
CREATE INDEX IF NOT EXISTS idx_extracted_forms_url ON public.extracted_forms(url_id);
CREATE INDEX IF NOT EXISTS idx_tech_fingerprints_url ON public.technology_fingerprints(url_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_user ON public.dashboard_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_name ON public.dashboard_metrics(metric_name);

-- Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scan_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.discovered_urls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.technology_fingerprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dashboard_metrics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for profiles
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Create RLS policies for projects
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

-- Create RLS policies for scan_sessions
CREATE POLICY "Users can view scans for their projects"
    ON public.scan_sessions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects 
            WHERE projects.id = scan_sessions.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can create scans for their projects"
    ON public.scan_sessions FOR INSERT
    WITH CHECK (
        auth.uid() = created_by AND
        EXISTS (
            SELECT 1 FROM public.projects 
            WHERE projects.id = scan_sessions.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can update scans for their projects"
    ON public.scan_sessions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.projects 
            WHERE projects.id = scan_sessions.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete scans for their projects"
    ON public.scan_sessions FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.projects 
            WHERE projects.id = scan_sessions.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

-- Create RLS policies for discovered_urls
CREATE POLICY "Users can view URLs from their scans"
    ON public.discovered_urls FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.scan_sessions 
            JOIN public.projects ON scan_sessions.project_id = projects.id
            WHERE scan_sessions.id = discovered_urls.session_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert URLs for their scans"
    ON public.discovered_urls FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.scan_sessions 
            JOIN public.projects ON scan_sessions.project_id = projects.id
            WHERE scan_sessions.id = discovered_urls.session_id 
            AND projects.owner_id = auth.uid()
        )
    );

-- Create RLS policies for extracted_forms
CREATE POLICY "Users can view forms from their scans"
    ON public.extracted_forms FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls
            JOIN public.scan_sessions ON discovered_urls.session_id = scan_sessions.id
            JOIN public.projects ON scan_sessions.project_id = projects.id
            WHERE discovered_urls.id = extracted_forms.url_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert forms for their scans"
    ON public.extracted_forms FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.discovered_urls
            JOIN public.scan_sessions ON discovered_urls.session_id = scan_sessions.id
            JOIN public.projects ON scan_sessions.project_id = projects.id
            WHERE discovered_urls.id = extracted_forms.url_id 
            AND projects.owner_id = auth.uid()
        )
    );

-- Create RLS policies for technology_fingerprints
CREATE POLICY "Users can view tech fingerprints from their scans"
    ON public.technology_fingerprints FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.discovered_urls
            JOIN public.scan_sessions ON discovered_urls.session_id = scan_sessions.id
            JOIN public.projects ON scan_sessions.project_id = projects.id
            WHERE discovered_urls.id = technology_fingerprints.url_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert tech fingerprints for their scans"
    ON public.technology_fingerprints FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.discovered_urls
            JOIN public.scan_sessions ON discovered_urls.session_id = scan_sessions.id
            JOIN public.projects ON scan_sessions.project_id = projects.id
            WHERE discovered_urls.id = technology_fingerprints.url_id 
            AND projects.owner_id = auth.uid()
        )
    );

-- Create RLS policies for dashboard_metrics
CREATE POLICY "Users can view their own metrics"
    ON public.dashboard_metrics FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own metrics"
    ON public.dashboard_metrics FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own metrics"
    ON public.dashboard_metrics FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own metrics"
    ON public.dashboard_metrics FOR DELETE
    USING (auth.uid() = user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON public.profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON public.projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, avatar_url)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'avatar_url');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Insert some sample data for testing (optional)
-- This will be executed only if the tables are empty

-- Note: Actual user data will be created through Supabase Auth
-- Sample projects and scans can be created through the API

COMMENT ON TABLE public.profiles IS 'Extended user profiles with additional metadata';
COMMENT ON TABLE public.projects IS 'Vulnerability scanning projects';
COMMENT ON TABLE public.scan_sessions IS 'Individual scan sessions within projects';
COMMENT ON TABLE public.discovered_urls IS 'URLs discovered during scanning';
COMMENT ON TABLE public.extracted_forms IS 'Forms extracted from discovered URLs';
COMMENT ON TABLE public.technology_fingerprints IS 'Technology stack detected on URLs';
COMMENT ON TABLE public.dashboard_metrics IS 'Custom dashboard metrics and KPIs';