import { Client } from 'pg';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

// Load env vars
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runMigration() {
  console.log('Starting migration...');

  // Try to find the connection string
  // Supabase usually provides DATABASE_URL in .env
  const connectionString = process.env.DATABASE_URL;

  if (!connectionString) {
    console.error('Error: DATABASE_URL not found in .env');
    process.exit(1);
  }

  // Handle Supabase "Transaction" vs "Session" mode pooling issues if necessary,
  // but usually standard connection string works for migrations if direct connection.
  // If it's port 6543 (transaction pooler), we can't run some statements, but usually 5432 is direct.

  const client = new Client({
    connectionString: connectionString,
    ssl: { rejectUnauthorized: false }, // Required for Supabase
  });

  try {
    await client.connect();
    console.log('Connected to database.');

    const sqlPath = path.join(__dirname, 'supabase', 'get_scan_report_rpc.sql');
    const sql = fs.readFileSync(sqlPath, 'utf8');

    console.log(`Reading migration file: ${sqlPath}`);
    // console.log(sql);

    await client.query(sql);
    console.log('Migration executed successfully!');
  } catch (err) {
    console.error('Migration failed:', err);
  } finally {
    await client.end();
  }
}

runMigration();
