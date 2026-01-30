-- Enhanced Scan Report RPC
-- Returns comprehensive scan report data with severity distribution, 
-- vulnerability types, and scan metrics for the report UI
-- FIXED: Uses 'title' as proxy for type/category since those columns don't exist

-- Drop existing function first
drop function if exists get_scan_report(uuid);

-- Create enhanced version
create or replace function get_scan_report(scan_uuid uuid)
returns jsonb as $$
declare
  result jsonb;
  v_created_at timestamptz;
  v_completed_at timestamptz;
  v_duration_seconds int;
begin
  -- Get scan timestamps for duration calculation
  select created_at, completed_at 
  into v_created_at, v_completed_at
  from scans where id = scan_uuid;
  
  -- Calculate duration in seconds
  if v_completed_at is not null and v_created_at is not null then
    v_duration_seconds := extract(epoch from (v_completed_at - v_created_at))::int;
  else
    v_duration_seconds := 0;
  end if;

  select jsonb_build_object(
    'id', s.id,
    'project_id', s.project_id,
    'project_name', (select name from projects where id = s.project_id),
    'target_url', s.target_url,
    'status', s.status,
    'score', coalesce(s.score, 0),
    'config', s.config,
    'created_at', s.created_at,
    'completed_at', s.completed_at,
    'scan_duration_seconds', v_duration_seconds,
    
    -- Severity distribution
    'severity_distribution', (
      select jsonb_build_object(
        'critical', count(*) filter (where severity = 'critical'),
        'high', count(*) filter (where severity = 'high'),
        'medium', count(*) filter (where severity = 'medium'),
        'low', count(*) filter (where severity = 'low'),
        'info', count(*) filter (where severity = 'info')
      )
      from findings where scan_id = scan_uuid
    ),
    
    -- Vulnerability types distribution (top 10) - using 'title' as proxy for type
    'vulnerability_types', (
      select coalesce(
        jsonb_agg(
          jsonb_build_object(
            'name', vuln_title,
            'count', cnt
          ) order by cnt desc
        ),
        '[]'::jsonb
      )
      from (
        select 
          coalesce(title, 'Unknown') as vuln_title,
          count(*) as cnt
        from findings 
        where scan_id = scan_uuid
        group by title
        order by cnt desc
        limit 10
      ) sub
    ),
    
    -- All findings with details
    'findings', (
      select coalesce(jsonb_agg(
        jsonb_build_object(
          'id', f.id,
          'title', f.title,
          'description', f.description,
          'severity', f.severity,
          'status', coalesce(f.status, 'open'), -- Default to open if null
          'category', f.title, -- Use title as category since category column missing
          'cve_id', f.cve_id,
          'cvss_score', f.cvss_score,
          'remediation', f.remediation,
          'evidence', f.evidence,
          'reference_links', f.reference_links,
          'created_at', f.created_at
        ) order by 
          case f.severity 
            when 'critical' then 1 
            when 'high' then 2 
            when 'medium' then 3 
            when 'low' then 4 
            else 5 
          end
      ), '[]'::jsonb)
      from findings f
      where f.scan_id = scan_uuid
    ),
    
    -- Asset count
    'assets_count', (select count(*) from assets a where a.scan_id = scan_uuid)
    
  ) into result
  from scans s
  where s.id = scan_uuid;

  return result;
end;
$$ language plpgsql security definer;

-- Grant access to authenticated users
grant execute on function get_scan_report(uuid) to authenticated;
