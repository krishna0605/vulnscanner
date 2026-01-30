-- SECURITY HARDENING & DATA ISOLATION FIX
-- 1. Fix RLS on project_metrics (Was allowing access to ALL authenticated users)
-- 2. Convert RPCs to SECURITY INVOKER to enforce RLS

BEGIN;

-- 1. FIX project_metrics RLS
DROP POLICY IF EXISTS "Metrics viewable by authenticated users" ON public.project_metrics;

CREATE POLICY "Metrics viewable by project owners" 
ON public.project_metrics FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM public.projects 
    WHERE public.projects.id = public.project_metrics.project_id 
    AND public.projects.user_id = auth.uid()
  )
);

-- 1.1 FIX assets RLS (Was allowing access to ALL authenticated users)
DROP POLICY IF EXISTS "Assets are viewable by authenticated users" ON public.assets;

CREATE POLICY "Assets viewable by project owners" 
ON public.assets FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM public.projects 
    WHERE public.projects.id = public.assets.project_id 
    AND public.projects.user_id = auth.uid()
  )
);

-- 2. FIX RPCs (Switch to SECURITY INVOKER)

-- get_global_stats
CREATE OR REPLACE FUNCTION get_global_stats()
RETURNS jsonb AS $$
DECLARE
  v_total_scans int;
  v_total_projects int;
  v_high_severity int;
  v_critical_severity int;
  v_avg_score numeric;
BEGIN
  -- Count total scans (Respects RLS: Only scans for my projects)
  SELECT count(*) INTO v_total_scans FROM scans;
  
  -- Count total active projects (Respects RLS: Only my projects)
  SELECT count(*) INTO v_total_projects FROM projects;
  
  -- Aggregate metrics (Respects RLS: Only my project metrics)
  SELECT 
    sum(critical_count), 
    sum(high_count), 
    avg(security_score)
  INTO 
    v_critical_severity, 
    v_high_severity, 
    v_avg_score
  FROM project_metrics;

  RETURN jsonb_build_object(
    'total_scans', coalesce(v_total_scans, 0),
    'total_projects', coalesce(v_total_projects, 0),
    'critical_count', coalesce(v_critical_severity, 0),
    'high_count', coalesce(v_high_severity, 0),
    'avg_security_score', round(coalesce(v_avg_score, 100), 1)
  );
END;
$$ LANGUAGE plpgsql SECURITY INVOKER; -- CHANGED FROM SECURITY DEFINER

-- get_project_scan_summaries
CREATE OR REPLACE FUNCTION get_project_scan_summaries()
RETURNS TABLE (
  project_id uuid,
  project_name text,
  target_url text,
  last_scan_date timestamptz,
  last_scan_status text,
  critical_count int,
  high_count int,
  security_score int
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id AS project_id,
    p.name AS project_name,
    p.target_urls[1] AS target_url,
    s.created_at AS last_scan_date,
    s.status AS last_scan_status,
    coalesce(pm.critical_count, 0) AS critical_count,
    coalesce(pm.high_count, 0) AS high_count,
    coalesce(pm.security_score, 100) AS security_score
  FROM projects p
  LEFT JOIN project_metrics pm ON p.id = pm.project_id
  -- Join with latest scan for status and date
  LEFT JOIN LATERAL (
    SELECT status, created_at 
    FROM scans 
    WHERE scans.project_id = p.id 
    ORDER BY created_at DESC 
    LIMIT 1
  ) s ON TRUE
  ORDER BY s.created_at DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql SECURITY INVOKER; -- CHANGED FROM SECURITY DEFINER

-- get_recent_scans
CREATE OR REPLACE FUNCTION get_recent_scans(limit_count int DEFAULT 20)
RETURNS jsonb AS $$
DECLARE
  result jsonb;
BEGIN
  SELECT jsonb_agg(row_to_json(t)) INTO result
  FROM (
      SELECT 
        s.id,
        s.target_url,
        s.status,
        coalesce(s.score, 0) AS score,
        s.created_at,
        s.completed_at,
        jsonb_build_object('name', p.name) AS project,
        (SELECT count(*) FROM findings f WHERE f.scan_id = s.id) AS findings_count,
        (
            SELECT count(*) 
            FROM findings f 
            WHERE f.scan_id = s.id 
            AND (f.severity = 'high' OR f.severity = 'critical')
        ) AS high_severity_count
      FROM scans s
      JOIN projects p ON s.project_id = p.id
      WHERE s.status = 'completed'
      ORDER BY s.completed_at DESC NULLS LAST
      LIMIT limit_count
  ) t;

  RETURN coalesce(result, '[]'::jsonb);
END;
$$ LANGUAGE plpgsql SECURITY INVOKER; -- CHANGED FROM SECURITY DEFINER

-- get_scan_report
CREATE OR REPLACE FUNCTION get_scan_report(scan_uuid uuid)
RETURNS jsonb AS $$
DECLARE
  result jsonb;
  v_created_at timestamptz;
  v_completed_at timestamptz;
  v_duration_seconds int;
BEGIN
  -- Get scan timestamps (Will satisfy RLS because SECURITY INVOKER)
  SELECT created_at, completed_at 
  INTO v_created_at, v_completed_at
  FROM scans WHERE id = scan_uuid;
  
  -- Calculate duration
  IF v_completed_at IS NOT NULL AND v_created_at IS NOT NULL THEN
    v_duration_seconds := extract(epoch FROM (v_completed_at - v_created_at))::int;
  ELSE
    v_duration_seconds := 0;
  END IF;

  SELECT jsonb_build_object(
    'id', s.id,
    'project_id', s.project_id,
    'project_name', (SELECT name FROM projects WHERE id = s.project_id),
    'target_url', s.target_url,
    'status', s.status,
    'score', coalesce(s.score, 0),
    'config', s.config,
    'created_at', s.created_at,
    'completed_at', s.completed_at,
    'scan_duration_seconds', v_duration_seconds,
    
    'severity_distribution', (
      SELECT jsonb_build_object(
        'critical', count(*) FILTER (WHERE severity = 'critical'),
        'high', count(*) FILTER (WHERE severity = 'high'),
        'medium', count(*) FILTER (WHERE severity = 'medium'),
        'low', count(*) FILTER (WHERE severity = 'low'),
        'info', count(*) FILTER (WHERE severity = 'info')
      )
      FROM findings WHERE scan_id = scan_uuid
    ),
    
    'vulnerability_types', (
      SELECT coalesce(
        jsonb_agg(
          jsonb_build_object(
            'name', vuln_title,
            'count', cnt
          ) ORDER BY cnt DESC
        ),
        '[]'::jsonb
      )
      FROM (
        SELECT 
          coalesce(title, 'Unknown') AS vuln_title,
          count(*) AS cnt
        FROM findings 
        WHERE scan_id = scan_uuid
        GROUP BY title
        ORDER BY cnt DESC
        LIMIT 10
      ) sub
    ),
    
    'findings', (
      SELECT coalesce(jsonb_agg(
        jsonb_build_object(
          'id', f.id,
          'title', f.title,
          'description', f.description,
          'severity', f.severity,
          'status', coalesce(f.status, 'open'),
          'category', f.title, 
          'cve_id', f.cve_id,
          'cvss_score', f.cvss_score,
          'remediation', f.remediation,
          'evidence', f.evidence,
          'reference_links', f.reference_links,
          'created_at', f.created_at
        ) ORDER BY 
          CASE f.severity 
            WHEN 'critical' THEN 1 
            WHEN 'high' THEN 2 
            WHEN 'medium' THEN 3 
            WHEN 'low' THEN 4 
            ELSE 5 
          END
      ), '[]'::jsonb)
      FROM findings f
      WHERE f.scan_id = scan_uuid
    ),
    
    'assets_count', (SELECT count(*) FROM assets a WHERE a.scan_id = scan_uuid)
    
  ) INTO result
  FROM scans s
  WHERE s.id = scan_uuid;

  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY INVOKER; -- CHANGED FROM SECURITY DEFINER

COMMIT;
