-- Performance Indexes for VulnScanner
-- Run via Supabase SQL Editor or migration

-- Scans indexes (most queried table)
CREATE INDEX IF NOT EXISTS idx_scans_project_id ON scans(project_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);

-- Findings indexes (for reporting)
CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings(scan_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);

-- Assets indexes
CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_scan_id ON assets(scan_id);

-- Projects index
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_scans_project_status ON scans(project_id, status);
CREATE INDEX IF NOT EXISTS idx_findings_scan_severity ON findings(scan_id, severity);
