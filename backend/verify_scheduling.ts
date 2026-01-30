import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });

const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

// We can just check if the `is_scheduled` column exists by inserting a test row?
// Or checking the RPC.
// Let's just create a dummy "scheduled" scan and see if it persists.

const supabase = createClient(supabaseUrl, supabaseKey);

async function verify() {
  console.log('Verifying Scan Scheduling...');

  const { data, error } = await supabase
    .from('scans')
    .insert({
      project_id: '00000000-0000-0000-0000-000000000000', // Dummy
      target_url: 'http://test-schedule.example.com',
      status: 'pending',
      is_scheduled: true,
      schedule_cron: '0 0 * * *',
      next_run_at: new Date().toISOString(),
    })
    .select()
    .maybeSingle();

  // It fails with foreign key constraint probably?
  if (error) {
    if (error.code === '23503') console.log('✅ Connection Working (FK error expected)');
    else console.error('❌ Unexpected Error:', error);
  } else {
    console.log('✅ Scan Inserted:', data);
  }
}

verify();
