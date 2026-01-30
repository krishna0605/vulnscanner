const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

const SQL = `
-- Phase 1: Collaboration (Comments)

-- 1. Create Table
create table if not exists finding_comments (
  id uuid default gen_random_uuid() primary key,
  finding_id uuid references findings(id) on delete cascade not null,
  user_id uuid references auth.users(id) on delete cascade not null,
  content text not null,
  created_at timestamptz default now()
);

-- 2. RLS Policies
alter table finding_comments enable row level security;

drop policy if exists "Comments are viewable by everyone" on finding_comments;
create policy "Comments are viewable by everyone" on finding_comments
  for select using (true);

drop policy if exists "Users can insert their own comments" on finding_comments;
create policy "Users can insert their own comments" on finding_comments
  for insert with check (auth.uid() = user_id);

-- 3. RPC: Get Comments
create or replace function get_finding_comments(finding_uuid uuid)
returns table (
  id uuid,
  content text,
  created_at timestamptz,
  user_email text
) as $$
begin
  return query
  select 
    c.id,
    c.content,
    c.created_at,
    coalesce(u.email::text, 'Unknown User') as user_email
  from finding_comments c
  left join auth.users u on c.user_id = u.id
  where c.finding_id = finding_uuid
  order by c.created_at desc;
end;
$$ language plpgsql security definer;

-- 4. RPC: Add Comment
create or replace function add_finding_comment(finding_uuid uuid, comment_content text)
returns jsonb as $$
declare
  new_comment record;
  user_email_text text;
  current_user_id uuid;
begin
  current_user_id := auth.uid();
  
  -- If no auth user (e.g. running from service role in dev or unauth), handle gracefully
  -- Ideally frontend is always creating this as authenticated user.
  -- For this script, we assume caller is authenticated.
  
  select email into user_email_text from auth.users where id = current_user_id;

  insert into finding_comments (finding_id, user_id, content)
  values (finding_uuid, current_user_id, comment_content)
  returning id, content, created_at into new_comment;
  
  return jsonb_build_object(
    'id', new_comment.id,
    'content', new_comment.content,
    'created_at', new_comment.created_at,
    'user_email', user_email_text
  );
end;
$$ language plpgsql security definer;

grant execute on function get_finding_comments(uuid) to authenticated;
grant execute on function add_finding_comment(uuid, text) to authenticated;
grant execute on function get_finding_comments(uuid) to service_role;
grant execute on function add_finding_comment(uuid, text) to service_role;
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
    
    console.log('Executing SQL to create finding_comments and RPCs...');
    await client.query(SQL);
    console.log('Success! Phase 1 backend migration complete.');

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
