-- Users table (managed by Supabase Auth, but usually we extend profiles)
create table public.profiles (
  id uuid references auth.users not null,
  email text,
  username text,
  full_name text,
  avatar_url text,
  updated_at timestamp with time zone,
  primary key (id)
);

-- Projects (Workspaces)
create table public.projects (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  name text not null,
  description text,
  user_id uuid references public.profiles(id) not null
);

-- Scans
create table public.scans (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  project_id uuid references public.projects(id) on delete cascade not null,
  target_url text not null,
  status text default 'pending' check (status in ('pending', 'processing', 'completed', 'failed')),
  score int,
  findings_count int default 0
);

-- Vulnerabilities (Findings)
create table public.findings (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  scan_id uuid references public.scans(id) on delete cascade not null,
  type text not null,
  severity text check (severity in ('critical', 'high', 'medium', 'low', 'info')),
  description text,
  evidence text, -- JSON or text dump of where it was found
  status text default 'open' check (status in ('open', 'fixed', 'false_positive'))
);

-- Assets (Discovered URLs/Subdomains)
create table public.assets (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  project_id uuid references public.projects(id) on delete cascade not null,
  scan_id uuid references public.scans(id),
  url text not null,
  type text default 'page'
);

-- Enable Row Level Security (RLS)
alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.scans enable row level security;
alter table public.findings enable row level security;
alter table public.assets enable row level security;

-- Simple policies (can be refined later)
create policy "Users can view own profile" on public.profiles for select using (auth.uid() = id);
create policy "Users can update own profile" on public.profiles for update using (auth.uid() = id);

-- Projects policies
create policy "Users can view own projects" on public.projects for select using (auth.uid() = user_id);
create policy "Users can insert own projects" on public.projects for insert with check (auth.uid() = user_id);

-- Scans policies (inherit project access ideally, or simple ownership check)
-- For now, assuming strict ownership chain isn't enforced by DB RLS for MVP backend access,
-- but good to have if we use Supabase client on frontend directly.
