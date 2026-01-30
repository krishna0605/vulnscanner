-- Fix Scans Type Constraint
-- The previous constraint likely didn't include 'standard' or 'deep'
DO $$
BEGIN
    -- Drop the constraint if it exists
    ALTER TABLE scans DROP CONSTRAINT IF EXISTS scans_type_check;
    
    -- Re-add the constraint with all valid profile types
    ALTER TABLE scans ADD CONSTRAINT scans_type_check 
    CHECK (type IN ('scan', 'quick', 'standard', 'deep', 'full')); 
    -- 'scan' was the default in phase1_scan_config.sql
    -- 'quick', 'standard', 'deep' from profiles
    -- 'full' just in case
END $$;
