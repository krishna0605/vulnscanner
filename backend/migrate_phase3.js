const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

const SQL = `
-- Phase 3: Ticket Integration

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

-- Only authenticated users can manage integrations
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

-- 4. RPC: Upsert Integration
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
grant execute on function upsert_integration(uuid, text, jsonb) to service_role;
`;

async function run() {
  console.log('Connecting...');
  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    console.log('Connected!');
    
    console.log('Executing SQL to create integrations table...');
    await client.query(SQL);
    console.log('Success! Phase 3 backend migration complete.');

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
