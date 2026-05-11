const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

const connectionString = process.env.DATABASE_URL || '';

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

