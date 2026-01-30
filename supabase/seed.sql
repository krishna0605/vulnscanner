-- ⚠️ PRE-REQUISITE: You must have at least one user signed up in your application.
-- This script picks the most recently created user to assign the dummy data to.

DO $$
DECLARE
  target_user_id uuid;
BEGIN
  -- Select the most recent user
  SELECT id INTO target_user_id FROM auth.users ORDER BY created_at DESC LIMIT 1;

  -- If no user exists, raise an error
  IF target_user_id IS NULL THEN
    RAISE EXCEPTION 'No users found in auth.users. Please sign up a user in your app first before running this seed.';
  END IF;

  -- 1. Projects
  INSERT INTO projects (id, name, description, target_urls, status, user_id)
  VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Main Production Cluster', 'Primary customer-facing application infrastructure.', ARRAY['https://app.vulnscanner.com', 'https://api.vulnscanner.com'], 'active', target_user_id),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'Legacy Marketing Site', 'Old Wordpress marketing site scheduled for deprecation.', ARRAY['https://blog.old-domain.com'], 'active', target_user_id),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'Dev Environment', 'Staging and testing servers.', ARRAY['https://staging.vulnscanner.com'], 'active', target_user_id)
  ON CONFLICT (id) DO NOTHING;

  -- 2. Scans
  INSERT INTO scans (id, project_id, status, type, score, started_at, completed_at)
  VALUES
    -- Completed Scan for Project A
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'completed', 'full', 85, NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 day'),
    -- In Progress Scan for Project A
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'scanning', 'quick', 0, NOW() - INTERVAL '1 hour', NULL),
    -- Failed Scan for Project B
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'failed', 'deep', 0, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days')
  ON CONFLICT (id) DO NOTHING;

  -- 3. Vulnerabilities (Linked to Completed Scan D)
  INSERT INTO vulnerabilities (scan_id, project_id, title, severity, description, status, cve_id)
  VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'SQL Injection in Login', 'critical', 'A SQL injection vulnerability was detected in the auth endpoint.', 'open', 'CVE-2023-0001'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Outdated NGINX Version', 'medium', 'The server is running an older version of NGINX with known minor issues.', 'open', 'CVE-2023-0045'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Cross-Site Scripting (XSS)', 'high', 'Reflected XSS found in search parameter.', 'fixed', 'CVE-2023-0022');
    -- No conflict handling needed for auto-generated UUIDs here usually, unless hardcoded IDs were used. 
    -- But here we didn't hardcode vulnerability IDs, so it's fine.

  -- 4. Activity Logs
  INSERT INTO activity_logs (user_id, action_type, description, created_at)
  VALUES
    (target_user_id, 'scan_completed', 'Completed full scan for Main Production Cluster', NOW() - INTERVAL '1 day'),
    (target_user_id, 'project_created', 'Created new project: Dev Environment', NOW() - INTERVAL '3 days'),
    (target_user_id, 'issue_found', 'Critical SQL Injection detected in Main Production Cluster', NOW() - INTERVAL '1 day'),
    (target_user_id, 'alert_trigger', 'High severity alert triggered for XSS vulnerability', NOW() - INTERVAL '1 day');

  -- 5. System Metrics (Last 24 hours sample) - These are public/global usually, but good to have
  INSERT INTO system_metrics (traffic_in_mbps, traffic_out_mbps, availability_score, timestamp)
  VALUES
    (45.2, 120.5, 99.9, NOW()),
    (42.1, 115.2, 99.9, NOW() - INTERVAL '1 hour'),
    (38.5, 98.4, 99.8, NOW() - INTERVAL '2 hours'),
    (35.2, 85.1, 100.0, NOW() - INTERVAL '3 hours'),
    (50.1, 130.2, 99.5, NOW() - INTERVAL '4 hours');

END $$;
