-- Add Metadata columns to Assets table for Crawler Parity
ALTER TABLE public.assets ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE public.assets ADD COLUMN IF NOT EXISTS status_code INT;
ALTER TABLE public.assets ADD COLUMN IF NOT EXISTS title TEXT;
