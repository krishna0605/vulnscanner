-- ==============================================
-- VulnScanner Complete Data Flow Fix
-- Run this in Supabase SQL Editor
-- ==============================================

-- =====================
-- 1. PROJECTS TABLE
-- =====================
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS target_urls TEXT[] DEFAULT '{}';
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS default_scan_profile TEXT;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS scan_frequency TEXT DEFAULT 'manual';
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS continuous_monitoring BOOLEAN DEFAULT false;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- =====================
-- 2. SCANS TABLE
-- =====================
ALTER TABLE public.scans ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;
-- Ensure 'type' column exists for easier filtering
ALTER TABLE public.scans ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'quick';

-- =====================
-- 3. ASSETS TABLE
-- =====================
ALTER TABLE public.assets ADD COLUMN IF NOT EXISTS status_code INTEGER;
ALTER TABLE public.assets ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE public.assets ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
-- Fix missing scan_id which caused the index error
ALTER TABLE public.assets ADD COLUMN IF NOT EXISTS scan_id UUID REFERENCES public.scans(id) ON DELETE CASCADE;

-- =====================
-- 4. VULNERABILITIES VIEW
-- =====================
-- This is the CRITICAL fix: creates a view that frontend can query
-- SAFE CLEANUP: robustly handle whether it's a table or view without errors
DO $$ 
BEGIN 
  -- 1. If it's a table, drop it
  IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'vulnerabilities') THEN
    DROP TABLE public.vulnerabilities CASCADE;
  END IF;
  
  -- 2. If it's a view, drop it
  IF EXISTS (SELECT FROM pg_views WHERE schemaname = 'public' AND viewname = 'vulnerabilities') THEN
    DROP VIEW public.vulnerabilities CASCADE;
  END IF;
END $$;

CREATE VIEW public.vulnerabilities AS
SELECT 
    f.id,
    f.scan_id,
    s.project_id,  -- Derived from join
    f.title,
    f.description,
    f.severity,
    COALESCE(f.status, 'open') as status,
    f.location,
    f.evidence,
    f.cve_id,
    f.cvss_score,
    f.cwe_id,
    f.remediation,
    f.reference_links,
    f.affected_assets,
    f.created_at
FROM public.findings f
JOIN public.scans s ON f.scan_id = s.id;

-- Grant access
GRANT SELECT ON public.vulnerabilities TO authenticated;
GRANT SELECT ON public.vulnerabilities TO anon;

-- =====================
-- 5. PERFORMANCE INDEXES
-- =====================
CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON public.findings(scan_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON public.findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_status ON public.findings(status);
CREATE INDEX IF NOT EXISTS idx_scans_project_id ON public.scans(project_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON public.scans(status);
CREATE INDEX IF NOT EXISTS idx_assets_scan_id ON public.assets(scan_id);
CREATE INDEX IF NOT EXISTS idx_assets_project_id ON public.assets(project_id);

-- =====================
-- 6. HELPER FUNCTIONS
-- =====================

-- Function to update project's updated_at on scan completion
CREATE OR REPLACE FUNCTION update_project_on_scan_complete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE projects 
        SET updated_at = NOW() 
        WHERE id = NEW.project_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update project
DROP TRIGGER IF EXISTS tr_update_project_on_scan ON public.scans;
CREATE TRIGGER tr_update_project_on_scan
AFTER UPDATE ON public.scans
FOR EACH ROW EXECUTE FUNCTION update_project_on_scan_complete();

-- =====================
-- 7. VERIFICATION QUERIES
-- =====================
-- After running, verify with:
-- SELECT * FROM vulnerabilities LIMIT 5;
-- SELECT id, status, completed_at FROM scans LIMIT 5;
-- SELECT id, name, target_urls, status FROM projects LIMIT 5;
