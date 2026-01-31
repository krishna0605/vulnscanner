import { Client } from 'pg';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

// Load env vars
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runSeed() {
  console.log('🌱 Starting profile seed...');

  const connectionString = process.env.DATABASE_URL;

  if (!connectionString) {
    console.error('❌ Error: DATABASE_URL not found in .env');
    process.exit(1);
  }

  const client = new Client({
    connectionString: connectionString,
    ssl: { rejectUnauthorized: false }, 
  });

  try {
    await client.connect();
    console.log('✅ Connected to database.');

    const sqlPath = path.join(__dirname, 'supabase', 'profiles_migration.sql');
    if (!fs.existsSync(sqlPath)) {
        console.error(`❌ SQL file not found at: ${sqlPath}`);
        process.exit(1);
    }

    const sql = fs.readFileSync(sqlPath, 'utf8');
    console.log(`📖 Reading seed file: ${sqlPath}`);

    await client.query(sql);
    console.log('🚀 Profiles seeded successfully!');
  } catch (err) {
    console.error('❌ Seed failed:', err);
  } finally {
    await client.end();
  }
}

runSeed();
