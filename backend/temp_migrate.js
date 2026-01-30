const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

async function run() {
  console.log('Connecting...');
  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    console.log('Connected!');
    
    const sqlPath = path.join(__dirname, 'supabase', 'get_scan_report_rpc.sql');
    console.log('Reading SQL from:', sqlPath);
    const sql = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('Executing query...');
    await client.query(sql);
    console.log('Success! RPC updated.');
  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
