-- Allow users to view assets belonging to projects they own
CREATE POLICY "Users can view assets of own projects" 
ON public.assets FOR SELECT 
USING (
  exists (
    select 1 from public.projects 
    where projects.id = assets.project_id 
    and projects.user_id = auth.uid()
  )
);

-- Allow users to insert assets into their projects (needed for crawler if running as user, or generally allowed)
CREATE POLICY "Users can insert assets to own projects" 
ON public.assets FOR INSERT 
WITH CHECK (
  exists (
    select 1 from public.projects 
    where projects.id = assets.project_id 
    and projects.user_id = auth.uid()
  )
);

-- Note: The crawler usually runs with Service Role key which bypasses RLS.
-- But the Frontend reading the report runs as the User, so SELECT policy is critical.
