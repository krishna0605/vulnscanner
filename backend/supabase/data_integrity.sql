-- URL validation constraint
ALTER TABLE scans 
ADD CONSTRAINT valid_target_url 
CHECK (target_url ~ '^https?://');

-- Severity validation (already exists, verify)
-- Score range validation
ALTER TABLE scans 
ADD CONSTRAINT valid_score_range 
CHECK (score IS NULL OR (score >= 0 AND score <= 100));

-- Timestamp validation (prevent future dates)
ALTER TABLE scans 
ADD CONSTRAINT valid_created_at 
CHECK (created_at <= now());

-- Function to auto-update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to profiles
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply to projects (add updated_at column first if missing)
ALTER TABLE projects ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
