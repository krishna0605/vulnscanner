const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

const SQL = `
SELECT id, target_url, status, progress, current_action, node FROM scans WHERE status IN ('queued', 'scanning', 'processing');
`;

async function run() {
  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    const res = await client.query(SQL);
    console.log('Active Scans in DB:');
    console.table(res.rows);
  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
