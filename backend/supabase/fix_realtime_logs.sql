-- Enable Realtime for scan_logs if not already enabled
-- This is critical for the Live Console to work

begin;

-- 1. Ensure the publication exists (standard supabase setup)
-- If it doesn't exist, we create it, but typically 'supabase_realtime' exists.
-- We safely add the table.

do $$
begin
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'scan_logs') then
    alter publication supabase_realtime add table public.scan_logs;
  end if;
  
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'scans') then
    alter publication supabase_realtime add table public.scans;
  end if;
  
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'findings') then
    alter publication supabase_realtime add table public.findings;
  end if;
end;
$$;

-- 2. Verify RLS (Row Level Security)
-- Realtime respects RLS. If RLS is on but no policy allows SELECT, realtime won't emit.

alter table public.scan_logs enable row level security;

-- Policy: Authenticated users can view logs
-- Drop first to avoid conflicts if re-running
drop policy if exists "Logs viewable by authenticated users" on public.scan_logs;

create policy "Logs viewable by authenticated users" 
on public.scan_logs for select 
to authenticated 
using (true);

-- Also allow Anon if you want public viewing (optional, kep secure for now)
-- create policy "Logs viewable by anon" on public.scan_logs for select to anon using (true);

commit;
