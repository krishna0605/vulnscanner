-- Phase 4: Active Scans Implementation

-- 1. Add Execution Tracking Columns to Scans
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'progress') THEN
        ALTER TABLE scans ADD COLUMN progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'current_action') THEN
        ALTER TABLE scans ADD COLUMN current_action TEXT DEFAULT 'Initializing';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'node') THEN
        ALTER TABLE scans ADD COLUMN node TEXT DEFAULT 'Default-Worker';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'started_at') THEN
        ALTER TABLE scans ADD COLUMN started_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- 2. Update RLS (if needed - scans are already RLS enabled, assuming public access or auth access)
-- No changes needed if existing policies cover update.

-- 3. Notify real-time listeners (Supabase does this automatically on UPDATE)
