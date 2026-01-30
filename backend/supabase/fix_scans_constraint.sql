-- Fix Scans Status Constraint
DO $$
BEGIN
    -- Drop the constraint if it exists (to reset it)
    ALTER TABLE scans DROP CONSTRAINT IF EXISTS scans_status_check;
    
    -- Re-add the constraint with confirmed valid values
    ALTER TABLE scans ADD CONSTRAINT scans_status_check 
    CHECK (status IN ('pending', 'queued', 'processing', 'scanning', 'completed', 'failed'));
END $$;
