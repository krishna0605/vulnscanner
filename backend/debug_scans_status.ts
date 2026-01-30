import { supabase } from './src/lib/supabase';

async function debugScans() {
  console.log('=== Debugging Scans ===\n');

  // 1. Check total scans count
  const { count: totalCount } = await supabase
    .from('scans')
    .select('*', { count: 'exact', head: true });
  console.log(`Total scans in DB: ${totalCount}`);

  // 2. Check scans by status
  const { data: statusCounts } = await supabase.from('scans').select('status');

  const statusMap: Record<string, number> = {};
  statusCounts?.forEach((s: any) => {
    statusMap[s.status] = (statusMap[s.status] || 0) + 1;
  });
  console.log('\nScans by status:');
  console.table(statusMap);

  // 3. Check if any scans have status = 'completed'
  const { data: completedScans, error: completeErr } = await supabase
    .from('scans')
    .select('id, status, project_id, target_url')
    .eq('status', 'completed')
    .limit(5);

  if (completeErr) {
    console.error('Error fetching completed scans:', completeErr);
  } else {
    console.log(`\nCompleted scans (first 5): ${completedScans?.length}`);
    if (completedScans && completedScans.length > 0) {
      console.table(completedScans);
    }
  }

  // 4. Test the RPC function directly
  console.log('\n--- Testing get_recent_scans RPC ---');
  const { data: rpcData, error: rpcError } = await supabase.rpc('get_recent_scans', {
    limit_count: 5,
  });

  if (rpcError) {
    console.error('RPC Error:', rpcError);
  } else {
    console.log(`RPC returned ${rpcData?.length || 0} scans:`);
    if (rpcData && rpcData.length > 0) {
      console.log(JSON.stringify(rpcData[0], null, 2));
    } else {
      console.log('RPC returned empty array or null');
    }
  }

  // 5. Check all distinct status values
  const { data: allStatuses } = await supabase.from('scans').select('status').limit(100);

  const uniqueStatuses = [...new Set(allStatuses?.map((s: any) => s.status))];
  console.log('\nAll unique status values in DB:', uniqueStatuses);
}

debugScans();
