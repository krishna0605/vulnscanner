const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

const SQL = `
-- RPC to get detailed information for a single finding
drop function if exists get_finding_details(uuid);

create or replace function get_finding_details(finding_uuid uuid)
returns jsonb as $$
declare
  result jsonb;
begin
  select jsonb_build_object(
    'id', f.id,
    'scan_id', f.scan_id,
    'project_id', s.project_id,
    'project_name', p.name,
    'scan_created_at', s.created_at,
    'title', f.title,
    'description', f.description,
    'severity', f.severity,
    'status', f.status,
    'cve_id', f.cve_id,
    'cwe_id', f.cwe_id,
    'cvss_score', f.cvss_score,
    'location', f.location,
    'evidence', f.evidence,
    'remediation', f.remediation,
    'reference_links', f.reference_links,
    'affected_assets', f.affected_assets,
    'created_at', f.created_at
  ) into result
  from findings f
  join scans s on f.scan_id = s.id
  join projects p on s.project_id = p.id
  where f.id = finding_uuid;

  return result;
end;
$$ language plpgsql security definer;

grant execute on function get_finding_details(uuid) to authenticated;
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
    
    console.log('Executing SQL to create get_finding_details RPC...');
    await client.query(SQL);
    console.log('Success! RPC created via embedded SQL.');

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
