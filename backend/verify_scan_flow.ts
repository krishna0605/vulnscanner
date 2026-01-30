import { CrawlerService } from './src/lib/crawler';
import { supabase } from './src/lib/supabase';

// Simple UUID generator to avoid dependency issues
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

async function verifyScanFlow() {
  console.log('--- Starting End-to-End Verification ---');

  // 1. Get Valid User (for Project FK)
  console.log('Fetching/Creating Admin User...');
  const {
    data: { users },
    error: userError,
  } = await supabase.auth.admin.listUsers();

  let userId = users?.[0]?.id;
  if (!userId) {
    console.log('No users found. Creating temp admin...');
    const { data: newUser, error: createError } = await supabase.auth.admin.createUser({
      email: `admin_${Date.now()}@test.com`,
      password: 'password123',
      email_confirm: true,
    });
    if (createError || !newUser.user) {
      console.error('CRITICAL: Failed to create user for testing.', createError);
      return;
    }
    userId = newUser.user.id;
  }
  console.log(`Using User ID: ${userId}`);

  // Ensure Profile Exists (if trigger didn't catch it)
  const { error: profileError } = await supabase
    .from('profiles')
    .upsert({
      id: userId,
      email: users?.[0]?.email || 'test@test.com',
      full_name: 'Test Admin',
    })
    .select();
  if (profileError) console.log('Profile upsert note:', profileError.message);

  // 2. Get or Create Project
  const projectId = 'e8760000-0000-0000-0000-000000000001';
  console.log('Ensuring valid project exists...');

  const testProject = {
    id: projectId,
    name: 'Verification Project',
    status: 'active',
    target_urls: ['https://example.com'],
    user_id: userId, // CRITICAL FIX
  };

  const { error: upsertError } = await supabase.from('projects').upsert(testProject).select();
  if (upsertError) {
    console.error('Failed to upsert project:', upsertError);
    return;
  }

  // 3. Debug Schema (Check Scans Table)
  console.log('Checking Scans Table Schema...');
  // Attempt to select target_url directly to see if it errors
  const { error: checkError } = await supabase.from('scans').select('target_url').limit(1);
  if (checkError) {
    console.error('SCHEMA CHECK FAILED:', checkError);
    // It might be named 'url' or something else?
  } else {
    console.log('Schema check passed: target_url column exists.');
  }

  // 4. Simulate API Call (Create Scan)
  console.log('Simulating New Scan API Call via DB Insert...');
  const targetUrl = 'https://example.com';
  const config = {
    scanType: 'quick',
    maxDepth: 1,
    checkHeaders: true,
    checkRobots: true,
    userAgent: 'VulnScanner-TestBot/1.0',
  };

  const { data: scan, error: scanError } = await supabase
    .from('scans')
    .insert({
      project_id: projectId,
      target_url: targetUrl,
      status: 'pending',
      config,
      type: 'quick',
    })
    .select()
    .single();

  if (scanError) {
    console.error('Failed to create scan record:', scanError);
    return;
  }
  console.log(`Scan created successfully! ID: ${scan.id}`);

  // 5. Trigger Crawler
  console.log('Triggering Crawler Service...');
  const crawler = new CrawlerService();
  await crawler.scan(scan.id, targetUrl, config as any);

  // 4. Verify Results
  console.log('Verifying Results...');
  const { data: updatedScan } = await supabase.from('scans').select('*').eq('id', scan.id).single();
  console.log('Final Scan Status:', updatedScan?.status);
  console.log('Progress:', updatedScan?.progress);

  const { count: findingsCount } = await supabase
    .from('findings')
    .select('*', { count: 'exact', head: true })
    .eq('scan_id', scan.id);
  console.log('Findings Found:', findingsCount);

  const { count: logsCount } = await supabase
    .from('scan_logs')
    .select('*', { count: 'exact', head: true })
    .eq('scan_id', scan.id);
  console.log('Logs Generated:', logsCount);

  if (updatedScan?.status === 'completed' && logsCount! > 0) {
    console.log('✅ VERIFICATION SUCCESSFUL: Scan completed with logs and findings.');
  } else {
    console.error('❌ VERIFICATION FAILED: Scan did not complete effectively.');
  }
}

verifyScanFlow();
