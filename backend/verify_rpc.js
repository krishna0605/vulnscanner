const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

async function run() {
  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    
    // Get a finding ID
    const res = await client.query('select id from findings limit 1');
    if (res.rows.length === 0) {
        console.log("No findings to test.");
        return;
    }
    const findingId = res.rows[0].id;
    console.log(`Testing RPC for finding ID: ${findingId}`);

    const rpcRes = await client.query(`select get_finding_details('${findingId}') as data`);
    console.log("RPC Result:", JSON.stringify(rpcRes.rows[0].data, null, 2));

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
