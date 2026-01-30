-- Soft Delete Pattern Implementation

-- Add deleted_at column to scans
ALTER TABLE scans ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Add deleted_at column to projects
ALTER TABLE projects ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Create view for active records
CREATE OR REPLACE VIEW active_scans AS
SELECT * FROM scans WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW active_projects AS
SELECT * FROM projects WHERE deleted_at IS NULL;

-- Update RLS policies to exclude soft-deleted records (Optional / Advanced)
-- NOTE: Changing policies on existing tables requires dropping and recreating them
-- or altering them securely. A simpler approach for MVP is filtering in app logic 
-- or using the views.

-- Example policy update (commented out for safety during migration script run):
-- CREATE POLICY "Hide deleted scans"
-- ON scans FOR SELECT
-- USING (deleted_at IS NULL);
