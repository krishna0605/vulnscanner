-- Function to fetch recent completed scans with summary metrics
-- Fixed: Calculate findings_count from findings table instead of non-existent column
create or replace function get_recent_scans(limit_count int default 20)
returns jsonb as $$
declare
  result jsonb;
begin
  select jsonb_agg(row_to_json(t)) into result
  from (
      select 
        s.id,
        s.target_url,
        s.status,
        coalesce(s.score, 0) as score,
        s.created_at,
        s.completed_at,
        jsonb_build_object('name', p.name) as project,
        -- Calculate findings_count from findings table
        (select count(*) from findings f where f.scan_id = s.id) as findings_count,
        -- Calculate high severity count
        (
            select count(*) 
            from findings f 
            where f.scan_id = s.id 
            and (f.severity = 'high' or f.severity = 'critical')
        ) as high_severity_count
      from scans s
      join projects p on s.project_id = p.id
      where s.status = 'completed'
      order by s.completed_at desc nulls last
      limit limit_count
  ) t;

  return coalesce(result, '[]'::jsonb);
end;
$$ language plpgsql security definer;

-- Grant access
grant execute on function get_recent_scans(int) to authenticated;
