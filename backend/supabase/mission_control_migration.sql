-- Mission Control Dashboard Schema Extensions

-- 1. PROFILES (For Team Stats & Presence)
-- Links to auth.users, but public/readable for the team view
create table if not exists public.profiles (
  id uuid references auth.users on delete cascade not null primary key,
  full_name text,
  avatar_url text,
  role text default 'Viewer',
  last_seen_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Enable RLS
alter table public.profiles enable row level security;

-- Policies
create policy "Public profiles are viewable by everyone" 
on public.profiles for select using (true);

create policy "Users can insert their own profile" 
on public.profiles for insert with check (auth.uid() = id);

create policy "Users can update their own profile" 
on public.profiles for update using (auth.uid() = id);

-- Realtime
alter publication supabase_realtime add table public.profiles;


-- 2. ASSETS (For Attack Surface Visualization)
create table if not exists public.assets (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references public.projects(id) on delete cascade not null,
  type text not null check (type in ('api', 'database', 'frontend', 'storage', 'server')),
  identifier text not null, -- URL, IP, or Name
  risk_score int default 0, -- 0-100
  last_scanned_at timestamptz,
  created_at timestamptz default now()
);

alter table public.assets enable row level security;
create policy "Assets are viewable by authenticated users" 
on public.assets for select using (auth.role() = 'authenticated');


-- 3. PROJECT METRICS (Pre-calculated stats for the Dashboard)
create table if not exists public.project_metrics (
  project_id uuid references public.projects(id) on delete cascade primary key,
  security_score int default 100,
  open_vulnerabilities_count int default 0,
  critical_count int default 0,
  high_count int default 0,
  -- Foreign key to scans if exists, otherwise nullable
  updated_at timestamptz default now()
);

alter table public.project_metrics enable row level security;
create policy "Metrics viewable by authenticated users" 
on public.project_metrics for select using (auth.role() = 'authenticated');


-- 4. TRIGGERS & FUNCTIONS

-- Trigger to handle new user signup -> Create Profile
create or replace function public.handle_new_user() 
returns trigger as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (new.id, new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'avatar_url');
  return new;
end;
$$ language plpgsql security definer;

-- Trigger execution
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Helper function for updating metrics (stub)
create or replace function update_project_metrics(p_id uuid)
returns void as $$
declare
  v_crit int;
  v_high int;
  v_score int;
begin
  -- Count vulns
  select count(*) into v_crit from vulnerabilities where project_id = p_id and severity = 'critical' and status = 'open';
  select count(*) into v_high from vulnerabilities where project_id = p_id and severity = 'high' and status = 'open';
  
  -- Simple score formula
  v_score := 100 - (v_crit * 10) - (v_high * 5);
  if v_score < 0 then v_score := 0; end if;

  insert into project_metrics (project_id, security_score, critical_count, high_count, updated_at)
  values (p_id, v_score, v_crit, v_high, now())
  on conflict (project_id) do update set
    security_score = excluded.security_score,
    critical_count = excluded.critical_count,
    high_count = excluded.high_count,
    updated_at = now();
end;
$$ language plpgsql;
