import { supabase } from './src/lib/supabase';

async function listScans() {
  console.log('Listing Scans:');
  const { data: scans, error } = await supabase
    .from('scans')
    .select('id, target_url, status, created_at');

  if (error) {
    console.error('Error:', error);
    return;
  }

  if (!scans || scans.length === 0) {
    console.log('No scans found.');
    return;
  }

  console.table(scans);
}

listScans();
