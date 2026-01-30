-- Phase 1: Database Schema Enhancements

-- 1. Update scans table with type column
ALTER TABLE public.scans
ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'scan'; -- 'scan' (default), 'quick', 'deep', etc.

-- 2. Create scan_presets table
CREATE TABLE IF NOT EXISTS public.scan_presets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  config JSONB NOT NULL,
  is_default BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Insert default presets
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.scan_presets WHERE name = 'Quick Scan') THEN
        INSERT INTO public.scan_presets (name, description, config, is_default)
        VALUES ('Quick Scan', 'Checks headers and top-level page only.', '{"maxDepth": 0, "maxPages": 1, "checkHeaders": true}', true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.scan_presets WHERE name = 'Standard Scan') THEN
        INSERT INTO public.scan_presets (name, description, config, is_default)
        VALUES ('Standard Scan', 'Crawls up to 2 levels deep, checks for common vulnerabilities.', '{"maxDepth": 2, "maxPages": 50, "checkHeaders": true, "checkMixedContent": true}', false);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.scan_presets WHERE name = 'Deep Scan') THEN
        INSERT INTO public.scan_presets (name, description, config, is_default)
        VALUES ('Deep Scan', 'Thorough crawl (limit 200 pages), checks all heuristics.', '{"maxDepth": 5, "maxPages": 200, "checkHeaders": true, "checkMixedContent": true, "checkComments": true}', false);
    END IF;
END $$;
