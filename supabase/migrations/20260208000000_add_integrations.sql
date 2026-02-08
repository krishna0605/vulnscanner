-- Phase 3: Ticket Integration
-- Migration to add integrations table and upsert_integration RPC

-- 1. Create Integrations Table
create table if not exists integrations (
  id uuid default gen_random_uuid() primary key,
  project_id uuid references projects(id) on delete cascade not null,
  type text not null check (type in ('jira', 'github')),
  config jsonb not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(project_id, type)
);

-- 2. RLS Policies
alter table integrations enable row level security;

drop policy if exists "Integrations viewable by authenticated users" on integrations;
create policy "Integrations viewable by authenticated users" on integrations
  for select to authenticated using (true);

drop policy if exists "Integrations insertable by authenticated users" on integrations;
create policy "Integrations insertable by authenticated users" on integrations
  for insert to authenticated with check (true);

drop policy if exists "Integrations updatable by authenticated users" on integrations;
create policy "Integrations updatable by authenticated users" on integrations
  for update to authenticated using (true);

drop policy if exists "Integrations deletable by authenticated users" on integrations;
create policy "Integrations deletable by authenticated users" on integrations
  for delete to authenticated using (true);

-- 3. RPC: Upsert Integration
create or replace function upsert_integration(
  p_project_id uuid,
  p_type text,
  p_config jsonb
)
returns jsonb as $$
declare
  result jsonb;
begin
  insert into integrations (project_id, type, config, updated_at)
  values (p_project_id, p_type, p_config, now())
  on conflict (project_id, type)
  do update set 
    config = p_config,
    updated_at = now()
  returning jsonb_build_object('id', id, 'type', type) into result;
  
  return result;
end;
$$ language plpgsql security definer;

grant execute on function upsert_integration(uuid, text, jsonb) to authenticated;

-- 4. Add status column to findings if missing
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'findings' AND column_name = 'status'
  ) THEN
    ALTER TABLE findings ADD COLUMN status text DEFAULT 'open' 
      CHECK (status in ('open', 'fixed', 'false_positive'));
  END IF;
END $$;
