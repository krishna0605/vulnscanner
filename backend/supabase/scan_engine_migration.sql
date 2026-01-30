-- Scan Engine Schema Extensions

-- 1. SCANS TABLE (ENHANCED)
-- Adding configuration and progress tracking to the existing table
alter table public.scans add column if not exists config jsonb default '{}';
alter table public.scans add column if not exists progress int default 0; -- 0-100%
alter table public.scans add column if not exists current_action text; -- e.g. "Scanning /login"
alter table public.scans add column if not exists report_url text; -- Link to PDF
alter table public.scans add column if not exists initiated_by uuid references auth.users;

-- 2. SCAN LOGS (REAL-TIME TERMINAL)
-- For streaming "Hacker-style" logs to the UI
create table if not exists public.scan_logs (
  id bigint generated always as identity primary key,
  scan_id uuid references public.scans(id) on delete cascade not null,
  level text default 'info', -- 'info', 'warn', 'error', 'success'
  message text not null,
  timestamp timestamptz default now()
);

-- Enable Realtime for logs so the UI can stream them
alter publication supabase_realtime add table public.scan_logs;
alter table public.scan_logs enable row level security;
create policy "Logs viewable by authenticated users" 
on public.scan_logs for select using (auth.role() = 'authenticated');

-- 3. FINDINGS (DETAILED)
-- Ensure the findings table has all fields for a professional report
-- (Note: If table exists, these columns will be added if missing)
create table if not exists public.findings (
  id uuid default gen_random_uuid() primary key,
  scan_id uuid references public.scans(id) on delete cascade not null,
  title text not null,
  description text,
  severity text check (severity in ('critical', 'high', 'medium', 'low', 'info')),
  location text, -- URL or File path
  evidence text, -- JSON payload or snippet
  remediation text,
  cwe_id text,
  created_at timestamptz default now()
);

-- Add indexes for faster fetching
create index if not exists idx_scan_logs_scan_id on public.scan_logs(scan_id);
create index if not exists idx_findings_scan_id on public.findings(scan_id);

-- 4. HELPER FUNCTION: START SCAN
-- To be called by the API to initialize a scan
create or replace function start_scan_job(p_project_id uuid, p_target_url text, p_user_id uuid, p_config jsonb)
returns uuid as $$
declare
  v_scan_id uuid;
begin
  insert into public.scans (project_id, target_url, status, initiated_by, config, progress, current_action)
  values (p_project_id, p_target_url, 'queued', p_user_id, p_config, 0, 'Initializing...')
  returning id into v_scan_id;
  
  return v_scan_id;
end;
$$ language plpgsql;
