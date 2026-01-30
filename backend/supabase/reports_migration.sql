-- Reports Page Extensions

-- 1. GLOBAL STATS FUNCTION
-- Aggregates data for the top level stats cards
create or replace function get_global_stats()
returns jsonb as $$
declare
  v_total_scans int;
  v_total_projects int;
  v_high_severity int;
  v_critical_severity int;
  v_avg_score numeric;
begin
  -- Count total scans performed
  select count(*) into v_total_scans from scans;
  
  -- Count total active projects
  select count(*) into v_total_projects from projects;
  
  -- Aggregate current risk metrics from all projects
  select 
    sum(critical_count), 
    sum(high_count), 
    avg(security_score)
  into 
    v_critical_severity, 
    v_high_severity, 
    v_avg_score
  from project_metrics;

  return jsonb_build_object(
    'total_scans', coalesce(v_total_scans, 0),
    'total_projects', coalesce(v_total_projects, 0),
    'critical_count', coalesce(v_critical_severity, 0),
    'high_count', coalesce(v_high_severity, 0),
    'avg_security_score', round(coalesce(v_avg_score, 100), 1)
  );
end;
$$ language plpgsql security definer;

-- 2. PROJECT SUMMARIES FUNCTION
-- Returns list of projects with their latest scan status and metrics
create or replace function get_project_scan_summaries()
returns table (
  project_id uuid,
  project_name text,
  target_url text,
  last_scan_date timestamptz,
  last_scan_status text,
  critical_count int,
  high_count int,
  security_score int
) as $$
begin
  return query
  select 
    p.id as project_id,
    p.name as project_name,
    p.target_urls[1] as target_url,
    s.created_at as last_scan_date,
    s.status as last_scan_status,
    coalesce(pm.critical_count, 0) as critical_count,
    coalesce(pm.high_count, 0) as high_count,
    coalesce(pm.security_score, 100) as security_score
  from projects p
  left join project_metrics pm on p.id = pm.project_id
  -- Join with latest scan for status and date
  left join lateral (
    select status, created_at 
    from scans 
    where scans.project_id = p.id 
    order by created_at desc 
    limit 1
  ) s on true
  order by s.created_at desc nulls last;
end;
$$ language plpgsql security definer;

-- Grant permissions (Adjust based on your RLS requirements)
grant execute on function get_global_stats() to authenticated;
grant execute on function get_project_scan_summaries() to authenticated;
