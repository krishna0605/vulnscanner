import { supabase } from './src/lib/supabase';

async function testReportRPC() {
  console.log('=== Testing get_scan_report RPC ===\n');

  // First get a valid scan ID
  const { data: scans } = await supabase
    .from('scans')
    .select('id, status')
    .eq('status', 'completed')
    .limit(1);

  if (!scans || scans.length === 0) {
    console.log('No completed scans found to test with.');
    return;
  }

  const testScanId = scans[0].id;
  console.log(`Testing with scan ID: ${testScanId}\n`);

  // Test the RPC
  const { data, error } = await supabase.rpc('get_scan_report', { scan_uuid: testScanId });

  if (error) {
    console.error('RPC Error:', error);
    console.log('\n--- Error Details ---');
    console.log('Code:', error.code);
    console.log('Message:', error.message);
    console.log('Hint:', error.hint);
    return;
  }

  console.log('RPC Success!');
  console.log('\n--- Report Data ---');
  console.log(JSON.stringify(data, null, 2));
}

testReportRPC();
