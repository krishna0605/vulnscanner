import { Client } from 'pg';
import dotenv from 'dotenv';
dotenv.config();

async function check() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });
  try {
    await client.connect();
    const res = await client.query("SELECT to_regclass('public.scan_presets');");
    console.log('Table exists:', res.rows[0].to_regclass);
    await client.end();
  } catch (e) {
    console.error(e);
  }
}
check();
