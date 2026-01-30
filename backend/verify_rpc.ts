import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load env vars
dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function testRpc() {
  console.log('Testing get_global_stats RPC...');
  const { data, error } = await supabase.rpc('get_global_stats');

  if (error) {
    console.error('RPC Error:', error);
  } else {
    console.log('RPC Success! Data:', data);
  }

  console.log('Testing get_project_scan_summaries RPC...');
  const { data: projects, error: pError } = await supabase.rpc('get_project_scan_summaries');

  if (pError) {
    console.error('RPC Projects Error:', pError);
  } else {
    console.log(`RPC Projects Success! Found ${projects ? projects.length : 0} projects.`);
    if (projects && projects.length > 0) {
      console.log('First project sample:', projects[0]);
    }
  }
}

testRpc();
