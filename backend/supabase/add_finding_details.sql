-- Add rich details to findings table
ALTER TABLE public.findings ADD COLUMN IF NOT EXISTS cve_id TEXT;
ALTER TABLE public.findings ADD COLUMN IF NOT EXISTS cvss_score NUMERIC(3,1);
ALTER TABLE public.findings ADD COLUMN IF NOT EXISTS remediation TEXT;
ALTER TABLE public.findings ADD COLUMN IF NOT EXISTS reference_links JSONB DEFAULT '[]'::jsonb;
ALTER TABLE public.findings ADD COLUMN IF NOT EXISTS affected_assets JSONB DEFAULT '[]'::jsonb;
