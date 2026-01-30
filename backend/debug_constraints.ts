import { Client } from 'pg';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import path from 'path';

dotenv.config();

async function debugConstraints() {
  console.log('--- Debugging Constraints ---');

  const connectionString = process.env.DATABASE_URL;
  if (!connectionString) {
    console.error('Error: DATABASE_URL not found in .env');
    process.exit(1);
  }

  const client = new Client({
    connectionString: connectionString,
    ssl: { rejectUnauthorized: false },
  });

  try {
    await client.connect();
    console.log('Connected to database.');

    const res = await client.query(`
        SELECT conname, pg_get_constraintdef(oid) as definition
        FROM pg_constraint
        WHERE conrelid = 'public.scans'::regclass;
    `);

    console.log('Constraints on "public.scans":');
    res.rows.forEach((row) => {
      console.log(`[${row.conname}]: ${row.definition}`);
    });
  } catch (err) {
    console.error('Debug script failed:', err);
  } finally {
    await client.end();
  }
}

debugConstraints();
