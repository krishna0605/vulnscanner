const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

const SQL = `
-- Add missing status column if it doesn't exist
ALTER TABLE public.findings ADD COLUMN IF NOT EXISTS status text DEFAULT 'open';

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'findings' AND column_name = 'status';
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
    
    console.log('Adding missing status column...');
    const res = await client.query(SQL);
    console.log('Success! Status column check/creation complete.');
    console.log(res[1].rows); // Print verification result

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
