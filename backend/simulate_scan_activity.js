const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Krishna%402003%23kapoor@db.djiiorrvmonqdccnftyq.supabase.co:5432/postgres';

// Script to simulate a scanner updating a SPECIFIC scan
// We will look for the most recent "pending" or "scanning" scan that IS NOT the demo one.

async function run() {
  const client = new Client({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    await client.connect();
    
    // 1. Find the user's new scan (most recent, not demo)
    const findRes = await client.query(`
        SELECT id, target_url, status 
        FROM scans 
        WHERE target_url != 'https://demo-target.com' 
        ORDER BY created_at DESC 
        LIMIT 1
    `);

    if (findRes.rowCount === 0) {
        console.log('No user-created scan found to simulate.');
        return;
    }

    const scan = findRes.rows[0];
    console.log(`Found User Scan: ${scan.id} (${scan.target_url}) [${scan.status}]`);

    // 2. Simulate Progress Loop
    const updates = [
        { progress: 5, action: 'Resolving DNS...', status: 'processing' },
        { progress: 15, action: 'Port Scanning...', status: 'scanning' },
        { progress: 30, action: 'Crawling /admin...', status: 'scanning' },
        { progress: 45, action: 'Crawling /api/v1...', status: 'scanning' },
        { progress: 60, action: 'Analyzing Responses...', status: 'scanning' },
        { progress: 80, action: 'Verifying Vulnerabilities...', status: 'scanning' },
        { progress: 95, action: 'Generating Report...', status: 'processing' },
        { progress: 100, action: 'Completed', status: 'completed' }
    ];

    for (const update of updates) {
        console.log(`-> Updating scan to ${update.progress}%: ${update.action}`);
        
        await client.query(`
            UPDATE scans 
            SET 
                progress = $1, 
                current_action = $2, 
                status = $3,
                updated_at = NOW()
            WHERE id = $4
        `, [update.progress, update.action, update.status, scan.id]);

        // Wait 2 seconds between updates to show animation
        await new Promise(r => setTimeout(r, 2000));
    }
    
    console.log('Simulation complete! Scan marked as completed.');

  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
  }
}

run();
