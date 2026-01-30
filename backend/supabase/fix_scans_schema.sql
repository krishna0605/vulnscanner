-- Fix Scans Table Schema
-- Ensure target_url exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'target_url') THEN
        ALTER TABLE scans ADD COLUMN target_url TEXT;
    END IF;
END $$;

-- Ensure config exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'config') THEN
        ALTER TABLE scans ADD COLUMN config JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- Ensure type exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'type') THEN
        ALTER TABLE scans ADD COLUMN type TEXT DEFAULT 'quick';
    END IF;
END $$;
