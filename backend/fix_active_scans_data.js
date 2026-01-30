const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

const UPD_SQL = `
UPDATE scans 
SET 
  progress = 45, 
  current_action = 'Fuzzing Endpoints',
  node = 'Worker-01',
  started_at = NOW(),
  target_url = COALESCE(target_url, 'https://demo-target.com')
WHERE status IN ('queued', 'scanning', 'processing');
`;

const INSERT_SQL = `
INSERT INTO scans (project_id, target_url, status, progress, current_action, node, type, started_at)
SELECT 
  id as project_id, 
  'https://demo-target.com' as target_url, 
  'scanning' as status, 
  10 as progress, 
  'Initializing Scan...' as current_action, 
  'Worker-01' as node, 
  'web' as type,
  NOW() as started_at
FROM projects 
LIMIT 1;
`;

// Helper to check if we updated anything
const CHECK_SQL = "SELECT count(*) as count FROM scans WHERE status IN ('queued', 'scanning', 'processing');";

async function run() {
  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    
    // 1. Try Update
    console.log('Attempting to fix existing active scans...');
    const res = await client.query(UPD_SQL);
    console.log(`Updated ${res.rowCount} rows.`);

    // 2. If no rows updated, insert a new one
    if (res.rowCount === 0) {
        console.log('No active scans found. Inserting a demo active scan...');
        const insertRes = await client.query(INSERT_SQL);
        console.log(`Inserted ${insertRes.rowCount} new scan.`);
    }

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
