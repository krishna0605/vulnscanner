-- =====================================================
-- ENHANCED VULNERABILITY SCANNER - SUPABASE SETUP
-- File 2: Core User and Authentication Tables
-- =====================================================
-- Run this file AFTER 01_extensions_and_types.sql
-- This creates core user management and authentication tables

-- =====================================================
-- USER MANAGEMENT TABLES
-- =====================================================

-- Extended user profiles (supplements Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    organization VARCHAR(100),
    job_title VARCHAR(100),
    phone VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    role user_role DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    phone_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    last_login_at TIMESTAMPTZ,
    last_login_ip INET,
    preferences JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API keys for programmatic access
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(20) NOT NULL,
    permissions JSONB DEFAULT '[]'::jsonb,
    rate_limit INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    last_used_ip INET,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User session tracking (optional - Supabase handles most of this)
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE,
    ip_address INET,
    user_agent TEXT,
    device_info JSONB DEFAULT '{}'::jsonb,
    location_info JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- BILLING AND SUBSCRIPTION TABLES
-- =====================================================

-- User subscriptions (for Stripe integration)
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    plan_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT false,
    canceled_at TIMESTAMPTZ,
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage tracking for billing
CREATE TABLE IF NOT EXISTS public.usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES public.subscriptions(id),
    metric_name VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    billing_period_start TIMESTAMPTZ,
    billing_period_end TIMESTAMPTZ
);

-- =====================================================
-- SYSTEM TABLES
-- =====================================================

-- System configuration and settings
CREATE TABLE IF NOT EXISTS public.system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,
    key VARCHAR(100) NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    updated_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(category, key)
);

-- Background job tracking
CREATE TABLE IF NOT EXISTS public.background_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,
    job_id VARCHAR(255) UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total INTEGER,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity and audit logs
CREATE TABLE IF NOT EXISTS public.activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    project_id UUID, -- Will reference projects table created later
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CONSTRAINTS AND CHECKS
-- =====================================================

-- Username constraints (add only if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_username_length') THEN
        ALTER TABLE public.profiles 
        ADD CONSTRAINT profiles_username_length CHECK (char_length(username) >= 3);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_username_format') THEN
        ALTER TABLE public.profiles 
        ADD CONSTRAINT profiles_username_format CHECK (username ~ '^[a-zA-Z0-9_-]+$');
    END IF;
END $$;

-- API key constraints (add only if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'api_keys_name_length') THEN
        ALTER TABLE public.api_keys 
        ADD CONSTRAINT api_keys_name_length CHECK (char_length(name) >= 3);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'api_keys_rate_limit_positive') THEN
        ALTER TABLE public.api_keys 
        ADD CONSTRAINT api_keys_rate_limit_positive CHECK (rate_limit > 0);
    END IF;
END $$;

-- Subscription status constraints (add only if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'subscriptions_valid_status') THEN
        ALTER TABLE public.subscriptions 
        ADD CONSTRAINT subscriptions_valid_status CHECK (
            status IN ('active', 'canceled', 'incomplete', 'incomplete_expired', 'past_due', 'trialing', 'unpaid')
        );
    END IF;
END $$;

-- Usage records constraints (add only if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'usage_records_quantity_positive') THEN
        ALTER TABLE public.usage_records 
        ADD CONSTRAINT usage_records_quantity_positive CHECK (quantity >= 0);
    END IF;
END $$;

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables (drop if exists first)
DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at 
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, avatar_url)
    VALUES (NEW.id, NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'avatar_url');
    RETURN NEW;
END;
$$ language 'plpgsql' SECURITY DEFINER;

-- Trigger to automatically create profile for new users (drop if exists first)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default system settings (skip if already exists)
INSERT INTO public.system_settings (category, key, value, description, is_public) VALUES
('scanning', 'default_timeout', '30', 'Default request timeout in seconds', true),
('scanning', 'max_concurrent_requests', '10', 'Maximum concurrent requests per scan', true),
('scanning', 'max_depth', '5', 'Maximum crawl depth', true),
('scanning', 'respect_robots_txt', 'true', 'Whether to respect robots.txt files', true),
('security', 'password_min_length', '8', 'Minimum password length', true),
('security', 'session_timeout', '3600', 'Session timeout in seconds', false),
('notifications', 'email_enabled', 'true', 'Whether email notifications are enabled', false),
('reports', 'max_report_size', '50', 'Maximum report size in MB', false),
('billing', 'free_tier_scan_limit', '10', 'Number of scans allowed in free tier', true),
('billing', 'free_tier_project_limit', '3', 'Number of projects allowed in free tier', true)
ON CONFLICT (category, key) DO NOTHING;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.profiles IS 'Extended user profiles supplementing Supabase auth.users';
COMMENT ON TABLE public.api_keys IS 'API keys for programmatic access to the platform';
COMMENT ON TABLE public.user_sessions IS 'User session tracking and device management';
COMMENT ON TABLE public.subscriptions IS 'User subscription and billing information';
COMMENT ON TABLE public.usage_records IS 'Usage tracking for billing and analytics';
COMMENT ON TABLE public.system_settings IS 'Global system configuration settings';
COMMENT ON TABLE public.background_jobs IS 'Background job execution tracking';
COMMENT ON TABLE public.activity_logs IS 'User activity and audit trail';

COMMENT ON COLUMN public.profiles.preferences IS 'User UI preferences and settings (JSON)';
COMMENT ON COLUMN public.profiles.metadata IS 'Additional user metadata and custom fields (JSON)';
COMMENT ON COLUMN public.api_keys.permissions IS 'Array of permission strings for API access';
COMMENT ON COLUMN public.api_keys.key_hash IS 'Hashed version of the API key for security';
COMMENT ON COLUMN public.user_sessions.device_info IS 'Device and browser information (JSON)';
COMMENT ON COLUMN public.user_sessions.location_info IS 'Geographic location data (JSON)';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment these to verify tables were created successfully:

-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('profiles', 'api_keys', 'user_sessions', 'subscriptions', 'usage_records', 'system_settings', 'background_jobs', 'activity_logs');
-- SELECT * FROM public.system_settings;

-- =====================================================
-- NEXT STEPS
-- =====================================================
-- After running this file successfully:
-- 1. Run 03_project_tables.sql for project management
-- 2. Run 04_scanning_tables.sql for scan execution
-- 3. Continue with remaining table creation files
-- 4. Apply RLS policies with 08_rls_policies.sql