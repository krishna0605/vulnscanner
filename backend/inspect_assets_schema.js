const { Client } = require('pg');

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
    
    // Check columns for assets table
    console.log('Fetching columns for ASSETS table...');
    const resultAssets = await client.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'assets'
    `);
    console.log('Columns in assets table:');
    resultAssets.rows.forEach(row => {
      console.log(`- ${row.column_name} (${row.data_type})`);
    });

    // Check columns for findings table (double check status)
    console.log('\nFetching columns for FINDINGS table...');
    const resultFindings = await client.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'findings'
    `);
    console.log('Columns in findings table:');
    resultFindings.rows.forEach(row => {
      console.log(`- ${row.column_name} (${row.data_type})`);
    });

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
