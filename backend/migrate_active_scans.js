const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

const SQL = `
-- Phase 4: Active Scans Implementation

-- 1. Add Execution Tracking Columns to Scans
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'progress') THEN
        ALTER TABLE scans ADD COLUMN progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'current_action') THEN
        ALTER TABLE scans ADD COLUMN current_action TEXT DEFAULT 'Initializing';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'node') THEN
        ALTER TABLE scans ADD COLUMN node TEXT DEFAULT 'Default-Worker';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'scans' AND column_name = 'started_at') THEN
        ALTER TABLE scans ADD COLUMN started_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;
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
    
    console.log('Executing SQL to add active scan columns...');
    await client.query(SQL);
    console.log('Success! Active Scans schema updated.');

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
