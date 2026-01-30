-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ⚠️ RESET ALL: Drop tables to ensure clean schema types (UUID vs Text conflicts)
-- This includes dropping 'projects' which cleans up the incompatible 'text' ID type.
drop table if exists activity_logs cascade;
drop table if exists system_metrics cascade;
drop table if exists vulnerabilities cascade;
drop table if exists findings cascade; 
drop table if exists scans cascade;
drop table if exists projects cascade; -- Force drop to fix "id text" issue

-- Projects Table (Recreated as UUID)
create table projects (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  name text not null,
  description text,
  target_urls text[] not null default '{}',
  status text not null default 'active' check (status in ('active', 'archived', 'maintenance')),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Scans Table
create table scans (
  id uuid default uuid_generate_v4() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  status text not null default 'queued' check (status in ('queued', 'scanning', 'completed', 'failed')),
  type text not null default 'quick' check (type in ('quick', 'full', 'deep', 'credentialed')),
  score int default 0,
  started_at timestamp with time zone default timezone('utc'::text, now()),
  completed_at timestamp with time zone,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Vulnerabilities Table
create table vulnerabilities (
  id uuid default uuid_generate_v4() primary key,
  scan_id uuid references scans(id) on delete cascade not null,
  project_id uuid references projects(id) on delete cascade not null,
  title text not null,
  severity text not null check (severity in ('critical', 'high', 'medium', 'low', 'info')),
  description text,
  status text not null default 'open' check (status in ('open', 'fixed', 'false_positive', 'ignored')),
  cve_id text,
  cvss_score float,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Activity Logs Table
create table activity_logs (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users(id) on delete set null,
  action_type text not null,
  description text not null,
  metadata jsonb default '{}'::jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- System Metrics Table (Time Series)
create table system_metrics (
  id uuid default uuid_generate_v4() primary key,
  traffic_in_mbps float default 0,
  traffic_out_mbps float default 0,
  availability_score float default 100.0,
  active_scans int default 0,
  timestamp timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Row Level Security (RLS) Policies

-- Projects
alter table projects enable row level security;
create policy "Users can view own projects" on projects for select using (auth.uid() = user_id);
create policy "Users can insert own projects" on projects for insert with check (auth.uid() = user_id);
create policy "Users can update own projects" on projects for update using (auth.uid() = user_id);
create policy "Users can delete own projects" on projects for delete using (auth.uid() = user_id);

-- Scans
alter table scans enable row level security;
create policy "Users can view scans of own projects" on scans for select using (
  exists (select 1 from projects where projects.id = scans.project_id and projects.user_id = auth.uid())
);
create policy "Users can insert scans for own projects" on scans for insert with check (
  exists (select 1 from projects where projects.id = scans.project_id and projects.user_id = auth.uid())
);

-- Vulnerabilities
alter table vulnerabilities enable row level security;
create policy "Users can view vulns of own projects" on vulnerabilities for select using (
  exists (select 1 from projects where projects.id = vulnerabilities.project_id and projects.user_id = auth.uid())
);

-- Activity Logs
alter table activity_logs enable row level security;
create policy "Users can view own logs" on activity_logs for select using (auth.uid() = user_id);
create policy "Users can insert own logs" on activity_logs for insert with check (auth.uid() = user_id);

-- System Metrics
alter table system_metrics enable row level security;
create policy "Everyone can view metrics" on system_metrics for select using (true);

-- Realtime subscription setup
do $$
begin
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'projects') then
    alter publication supabase_realtime add table projects;
  end if;
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'scans') then
    alter publication supabase_realtime add table scans;
  end if;
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'vulnerabilities') then
    alter publication supabase_realtime add table vulnerabilities;
  end if;
  -- Activity logs & metrics are optional for realtime, but good for "Live Feed"
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'activity_logs') then
    alter publication supabase_realtime add table activity_logs;
  end if;
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'system_metrics') then
    alter publication supabase_realtime add table system_metrics;
  end if;
end $$;
