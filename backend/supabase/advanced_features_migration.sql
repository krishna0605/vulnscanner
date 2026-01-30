-- Migration: Add Scheduling Logic to Scans Table

ALTER TABLE public.scans
ADD COLUMN IF NOT EXISTS is_scheduled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS schedule_cron TEXT NULL, -- e.g. "0 0 * * *" for daily
ADD COLUMN IF NOT EXISTS next_run_at TIMESTAMP WITH TIME ZONE NULL,
ADD COLUMN IF NOT EXISTS last_run_at TIMESTAMP WITH TIME ZONE NULL,
ADD COLUMN IF NOT EXISTS parent_scan_id UUID REFERENCES public.scans(id) ON DELETE SET NULL; -- If this key references a "Template Scan"

-- Index for scheduler polling
CREATE INDEX IF NOT EXISTS idx_scans_next_run_at ON public.scans(next_run_at) WHERE status = 'pending' AND is_scheduled = TRUE;
