-- =====================================================
-- ENHANCED VULNERABILITY SCANNER - SUPABASE SETUP
-- File 3: Project Management Tables
-- =====================================================
-- Run this file AFTER 02_core_tables.sql
-- This creates project management, team collaboration, and project configuration tables

-- =====================================================
-- PROJECT MANAGEMENT TABLES
-- =====================================================

-- Main projects table
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    target_domain VARCHAR(255) NOT NULL,
    target_urls JSONB DEFAULT '[]'::jsonb,
    scope_rules JSONB DEFAULT '[]'::jsonb,
    exclude_patterns JSONB DEFAULT '[]'::jsonb,
    visibility project_visibility DEFAULT 'private',
    is_active BOOLEAN DEFAULT true,
    is_archived BOOLEAN DEFAULT false,
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project team members and permissions
CREATE TABLE public.project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role user_role DEFAULT 'viewer',
    permissions JSONB DEFAULT '[]'::jsonb,
    invited_by UUID REFERENCES auth.users(id),
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    joined_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(project_id, user_id)
);

-- Project-specific settings and configurations
CREATE TABLE public.project_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_inherited BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, category)
);

-- Scan configurations (reusable templates)
CREATE TABLE public.scan_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    scan_type scan_type DEFAULT 'discovery',
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- PROJECT COLLABORATION TABLES
-- =====================================================

-- Project invitations
CREATE TABLE public.project_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'viewer',
    permissions JSONB DEFAULT '[]'::jsonb,
    invitation_token VARCHAR(255) UNIQUE NOT NULL,
    invited_by UUID REFERENCES auth.users(id),
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    declined_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project comments and notes
CREATE TABLE public.project_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES public.project_comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    is_resolved BOOLEAN DEFAULT false,
    resolved_by UUID REFERENCES auth.users(id),
    resolved_at TIMESTAMPTZ,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project favorites/bookmarks
CREATE TABLE public.project_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, user_id)
);

-- =====================================================
-- PROJECT ANALYTICS TABLES
-- =====================================================

-- Project activity tracking
CREATE TABLE public.project_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project statistics and metrics
CREATE TABLE public.project_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    total_scans INTEGER DEFAULT 0,
    total_urls_discovered INTEGER DEFAULT 0,
    total_vulnerabilities INTEGER DEFAULT 0,
    critical_vulnerabilities INTEGER DEFAULT 0,
    high_vulnerabilities INTEGER DEFAULT 0,
    medium_vulnerabilities INTEGER DEFAULT 0,
    low_vulnerabilities INTEGER DEFAULT 0,
    info_vulnerabilities INTEGER DEFAULT 0,
    last_scan_date TIMESTAMPTZ,
    last_vulnerability_date TIMESTAMPTZ,
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CONSTRAINTS AND CHECKS
-- =====================================================

-- Project name constraints
ALTER TABLE public.projects 
ADD CONSTRAINT projects_name_length CHECK (char_length(name) >= 3);

-- Target domain validation
ALTER TABLE public.projects 
ADD CONSTRAINT projects_target_domain_format CHECK (
    target_domain ~ '^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
);

-- Project member role validation
ALTER TABLE public.project_members 
ADD CONSTRAINT project_members_valid_role CHECK (
    role IN ('admin', 'user', 'viewer', 'analyst', 'manager')
);

-- Scan configuration name constraints
ALTER TABLE public.scan_configurations 
ADD CONSTRAINT scan_configurations_name_length CHECK (char_length(name) >= 3);

-- Project invitation expiry validation
ALTER TABLE public.project_invitations 
ADD CONSTRAINT project_invitations_expires_future CHECK (expires_at > created_at);

-- Comment content validation
ALTER TABLE public.project_comments 
ADD CONSTRAINT project_comments_content_length CHECK (char_length(content) >= 1);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON public.projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_settings_updated_at 
    BEFORE UPDATE ON public.project_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scan_configurations_updated_at 
    BEFORE UPDATE ON public.scan_configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_comments_updated_at 
    BEFORE UPDATE ON public.project_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically add project owner as admin member
CREATE OR REPLACE FUNCTION add_project_owner_as_member()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.project_members (project_id, user_id, role, joined_at)
    VALUES (NEW.id, NEW.owner_id, 'admin', NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to add project owner as admin member
CREATE TRIGGER on_project_created
    AFTER INSERT ON public.projects
    FOR EACH ROW EXECUTE FUNCTION add_project_owner_as_member();

-- Function to update project statistics
CREATE OR REPLACE FUNCTION update_project_statistics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.project_statistics (project_id, calculated_at)
    VALUES (NEW.project_id, NOW())
    ON CONFLICT (project_id) DO UPDATE SET
        calculated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate invitation token
CREATE OR REPLACE FUNCTION generate_invitation_token()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.invitation_token IS NULL THEN
        NEW.invitation_token := encode(gen_random_bytes(32), 'hex');
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to generate invitation token
CREATE TRIGGER generate_invitation_token_trigger
    BEFORE INSERT ON public.project_invitations
    FOR EACH ROW EXECUTE FUNCTION generate_invitation_token();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Project members with user details
CREATE VIEW project_members_with_users AS
SELECT 
    pm.id,
    pm.project_id,
    pm.user_id,
    pm.role,
    pm.permissions,
    pm.joined_at,
    pm.is_active,
    p.username,
    p.full_name,
    p.avatar_url,
    p.organization
FROM public.project_members pm
JOIN public.profiles p ON pm.user_id = p.id
WHERE pm.is_active = true;

-- Project overview with statistics
CREATE VIEW project_overview AS
SELECT 
    p.id,
    p.name,
    p.description,
    p.target_domain,
    p.visibility,
    p.is_active,
    p.created_at,
    p.updated_at,
    owner.username as owner_username,
    owner.full_name as owner_name,
    COALESCE(ps.total_scans, 0) as total_scans,
    COALESCE(ps.total_vulnerabilities, 0) as total_vulnerabilities,
    COALESCE(ps.critical_vulnerabilities, 0) as critical_vulnerabilities,
    ps.last_scan_date,
    (SELECT COUNT(*) FROM public.project_members WHERE project_id = p.id AND is_active = true) as member_count
FROM public.projects p
JOIN public.profiles owner ON p.owner_id = owner.id
LEFT JOIN public.project_statistics ps ON p.id = ps.project_id;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE public.projects IS 'Main projects table for vulnerability scanning targets';
COMMENT ON TABLE public.project_members IS 'Project team members and their roles/permissions';
COMMENT ON TABLE public.project_settings IS 'Project-specific configuration settings';
COMMENT ON TABLE public.scan_configurations IS 'Reusable scan configuration templates';
COMMENT ON TABLE public.project_invitations IS 'Pending project invitations';
COMMENT ON TABLE public.project_comments IS 'Project comments and collaboration notes';
COMMENT ON TABLE public.project_favorites IS 'User bookmarks for projects';
COMMENT ON TABLE public.project_activity IS 'Project activity and change tracking';
COMMENT ON TABLE public.project_statistics IS 'Cached project statistics and metrics';

COMMENT ON COLUMN public.projects.scope_rules IS 'JSON array of regex patterns defining scan scope';
COMMENT ON COLUMN public.projects.exclude_patterns IS 'JSON array of patterns to exclude from scanning';
COMMENT ON COLUMN public.projects.target_urls IS 'JSON array of specific URLs to target';
COMMENT ON COLUMN public.projects.tags IS 'JSON array of project tags for organization';
COMMENT ON COLUMN public.project_members.permissions IS 'JSON array of specific permissions granted';
COMMENT ON COLUMN public.scan_configurations.configuration IS 'JSON object with scan parameters';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Uncomment these to verify tables were created successfully:

-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'project%';
-- SELECT * FROM project_overview LIMIT 5;

-- =====================================================
-- NEXT STEPS
-- =====================================================
-- After running this file successfully:
-- 1. Run 04_scanning_tables.sql for scan execution tables
-- 2. Run 05_vulnerability_tables.sql for vulnerability management
-- 3. Continue with remaining table creation files
-- 4. Apply RLS policies with 08_rls_policies.sql