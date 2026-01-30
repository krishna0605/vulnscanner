-- Enable RLS (idempotent)
ALTER TABLE public.scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

-- SCANS POLICIES
DROP POLICY IF EXISTS "Users can view scans of own projects" ON public.scans;
DROP POLICY IF EXISTS "Users can insert scans to own projects" ON public.scans;
DROP POLICY IF EXISTS "Users can update scans of own projects" ON public.scans;

CREATE POLICY "Users can view scans of own projects" 
ON public.scans FOR SELECT 
USING (
  exists (
    select 1 from public.projects 
    where projects.id = scans.project_id 
    and projects.user_id = auth.uid()
  )
);

CREATE POLICY "Users can insert scans to own projects" 
ON public.scans FOR INSERT 
WITH CHECK (
  exists (
    select 1 from public.projects 
    where projects.id = scans.project_id 
    and projects.user_id = auth.uid()
  )
);

CREATE POLICY "Users can update scans of own projects" 
ON public.scans FOR UPDATE
USING (
  exists (
    select 1 from public.projects 
    where projects.id = scans.project_id 
    and projects.user_id = auth.uid()
  )
);

-- FINDINGS POLICIES
DROP POLICY IF EXISTS "Users can view findings of own scans" ON public.findings;

CREATE POLICY "Users can view findings of own scans" 
ON public.findings FOR SELECT 
USING (
  exists (
    select 1 from public.scans
    join public.projects on projects.id = scans.project_id
    where scans.id = findings.scan_id 
    and projects.user_id = auth.uid()
  )
);

-- ASSETS POLICIES
DROP POLICY IF EXISTS "Users can view assets of own projects" ON public.assets;
DROP POLICY IF EXISTS "Users can insert assets to own projects" ON public.assets;

CREATE POLICY "Users can view assets of own projects" 
ON public.assets FOR SELECT 
USING (
  exists (
    select 1 from public.projects 
    where projects.id = assets.project_id 
    and projects.user_id = auth.uid()
  )
);
