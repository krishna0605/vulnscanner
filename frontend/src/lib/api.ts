import { createClient } from '@/utils/supabase/server';
import { logger } from '@/utils/logger';
import { formatDistanceToNow } from 'date-fns';

// -- Types --

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived' | 'maintenance';
  target_urls: string[];
  item_count?: number; // Computed or joined
}

export interface Scan {
  id: string;
  project_id: string;
  status: 'queued' | 'scanning' | 'completed' | 'failed';
  type: 'quick' | 'full' | 'deep';
  score: number;
  started_at: string;
  completed_at?: string;
}

export interface Vulnerability {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'fixed' | 'false_positive';
  project_id: string;
}

export interface ActivityLog {
  id: string;
  user_id: string;
  action_type: string;
  description: string;
  created_at: string;
  user_email?: string; // Joined
}

export interface SystemMetric {
  timestamp: string;
  traffic_in: number;
  traffic_out: number;
}

// -- Graph Types --

export interface GraphNode {
  id: string;
  label: string;
  type: 'project' | 'scan' | 'vulnerability';
  val: number; // Visual size
  color: string;
  data?: any; // Original data payload
}

export interface GraphLink {
  source: string;
  target: string;
  color: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

// -- Fetchers --

export async function getDashboardStats() {
  const supabase = createClient();

  // 1. First, get the current user's project IDs
  const { data: userProjects, error: projectError } = await supabase.from('projects').select('id');

  if (projectError) {
    logger.error('Error fetching projects:', { error: projectError });
    throw new Error(`Failed to fetch dashboard data: ${projectError.message}`);
  }

  const projectIds = userProjects?.map((p) => p.id) || [];

  // If user has no projects, return zeros
  if (projectIds.length === 0) {
    return {
      securityScore: 0,
      activeThreats: 0,
      completedScans: 0,
      availability: null,
    };
  }

  // 2. Get ALL scans for user's projects
  const { data: userScans, error: scanError } = await supabase
    .from('scans')
    .select('id, score, status')
    .in('project_id', projectIds)
    .order('created_at', { ascending: false });

  if (scanError) {
    logger.error('Error fetching scans:', { error: scanError });
    throw new Error(`Failed to fetch scan data: ${scanError.message}`);
  }

  const scanIds = userScans?.map((s) => s.id) || [];
  const completedScansCount = userScans?.filter((s) => s.status === 'completed').length || 0;

  // 3. Count findings by severity
  let criticalCount = 0;
  let highCount = 0;
  let mediumCount = 0;
  let lowCount = 0;

  if (scanIds.length > 0) {
    const { data: findings, error: findingsError } = await supabase
      .from('findings')
      .select('severity')
      .in('scan_id', scanIds);

    if (findingsError) {
      logger.error('Error fetching findings:', { error: findingsError });
      // Don't throw here, just log, as we can estimate score without findings if needed, or better throw?
      // Let's throw to be safe/consistent.
      throw new Error(`Failed to fetch findings data: ${findingsError.message}`);
    }

    if (findings && findings.length > 0) {
      findings.forEach((f) => {
        if (f.severity === 'critical') criticalCount++;
        else if (f.severity === 'high') highCount++;
        else if (f.severity === 'medium') mediumCount++;
        else if (f.severity === 'low') lowCount++;
      });
    }
  }

  // Calculate security score
  const penalty = criticalCount * 15 + highCount * 8 + mediumCount * 3 + lowCount * 1;
  const estimatedScore = Math.max(0, Math.min(100, 100 - penalty));

  const dbScores = userScans?.filter((s) => s.score && s.score > 0) || [];
  let avgScore = estimatedScore;
  if (dbScores.length > 0) {
    const total = dbScores.reduce((acc, curr) => acc + (curr.score || 0), 0);
    avgScore = Math.floor(total / dbScores.length);
  }

  const activeThreats = criticalCount + highCount;

  // 4. Calculate Availability
  const failedScans = userScans?.filter((s) => s.status === 'failed').length || 0;
  const finishedScans = completedScansCount + failedScans;

  let availability: number | null = null;
  if (finishedScans > 0) {
    availability = Math.round((completedScansCount / finishedScans) * 1000) / 10;
  }

  return {
    securityScore: avgScore,
    activeThreats: activeThreats,
    completedScans: completedScansCount,
    availability: availability,
  };
}

export async function getNetworkMetrics() {
  const supabase = createClient();
  // Fetch last 24 points (e.g., hourly) - simplifying to just latest 20 rows for chart
  const { data } = await supabase
    .from('system_metrics')
    .select('timestamp, traffic_in_mbps, traffic_out_mbps')
    .order('timestamp', { ascending: true })
    .limit(20);

  return (
    data?.map((d) => ({
      created_at: d.timestamp,
      traffic_in: d.traffic_in_mbps,
      traffic_out: d.traffic_out_mbps,
    })) || []
  );
}

export async function getRecentActivity() {
  const supabase = createClient();

  // Try activity_logs first
  const { data: activityLogs } = await supabase
    .from('activity_logs')
    .select(
      `
            *,
            users:user_id (email)
        `
    )
    .order('created_at', { ascending: false })
    .limit(10);

  // If activity_logs has data, return it
  if (activityLogs && activityLogs.length > 0) {
    return activityLogs.map((log) => ({
      ...log,
      user_email: (log.users as any)?.email || 'System',
    }));
  }

  // FALLBACK: Generate activity from recent scans if activity_logs is empty
  const { data: recentScans } = await supabase
    .from('scans')
    .select(
      `
            id,
            status,
            type,
            created_at,
            completed_at,
            score,
            projects (name)
        `
    )
    .order('created_at', { ascending: false })
    .limit(10);

  if (!recentScans || recentScans.length === 0) {
    return [];
  }

  // Transform scans into activity-like entries
  return recentScans.map((scan) => {
    const projectName = (scan.projects as any)?.name || 'Unknown Project';
    let action_type = 'scan_completed';
    let description = '';

    if (scan.status === 'completed') {
      action_type = 'scan_completed';
      description = `Scan completed for ${projectName} with score ${scan.score ?? 'N/A'}`;
    } else if (scan.status === 'failed') {
      action_type = 'scan_failed';
      description = `Scan failed for ${projectName}`;
    } else if (scan.status === 'scanning') {
      action_type = 'scan_started';
      description = `Scan in progress for ${projectName}`;
    } else {
      action_type = 'scan_queued';
      description = `Scan queued for ${projectName}`;
    }

    return {
      id: scan.id,
      action_type,
      description,
      created_at: scan.completed_at || scan.created_at,
      user_email: 'System',
      metadata: { scan_id: scan.id, project_name: projectName },
    };
  });
}

export async function getDashboardProjects() {
  const supabase = createClient();

  // Fetch projects with their LATEST scan status
  // This is a bit complex in Supabase simple query, so we might multiple query or join.
  // For now, fetching projects and we can fetch latest status in a separate component or efficiently here.
  const { data: projects } = await supabase
    .from('projects')
    .select('*')
    .eq('status', 'active')
    .limit(5);

  return projects || [];
}

export async function getGraphData(): Promise<GraphData> {
  const supabase = createClient();

  // 1. Fetch User's Projects (RLS enforces ownership)
  const { data: projects } = await supabase.from('projects').select('id, name');
  if (!projects || projects.length === 0) return { nodes: [], links: [] };

  const projectIds = projects.map((p) => p.id);

  // 2. Fetch Recent Scans for user's projects (limit to 10 most recent)
  const { data: scans } = await supabase
    .from('scans')
    .select('id, project_id, status, type, score')
    .in('project_id', projectIds)
    .order('created_at', { ascending: false })
    .limit(10);

  // -- Build Simplified Graph (NO individual vulnerability nodes) --
  const nodes: GraphNode[] = [];
  const links: GraphLink[] = [];

  // Helper to add node if unique
  const addedNodes = new Set<string>();
  const addNode = (n: GraphNode) => {
    if (!addedNodes.has(n.id)) {
      nodes.push(n);
      addedNodes.add(n.id);
    }
  };

  // 0. Root Node (The Shield/Main System)
  const rootId = 'root-system';
  addNode({
    id: rootId,
    label: 'VulnScanner',
    type: 'root' as any,
    val: 8, // Larger root
    color: '#ffffff',
    data: { description: 'Central Command' },
  });

  // A. Projects (Connect to Root)
  projects.forEach((p) => {
    addNode({
      id: p.id,
      label: p.name,
      type: 'project',
      val: 6,
      color: '#0ea5e9', // Sky 500
      data: p,
    });
    links.push({ source: p.id, target: rootId, color: 'rgba(255,255,255,0.15)' });
  });

  // B. Scans (Colored by Score - Green/Yellow/Red)
  scans?.forEach((s) => {
    if (addedNodes.has(s.project_id)) {
      // Determine color based on scan score
      let color = '#8b5cf6'; // Default violet for in-progress
      if (s.status === 'completed' && s.score !== null) {
        if (s.score >= 80)
          color = '#22c55e'; // Green
        else if (s.score >= 50)
          color = '#eab308'; // Yellow
        else color = '#ef4444'; // Red
      } else if (s.status === 'failed') {
        color = '#6b7280'; // Gray for failed
      }

      addNode({
        id: s.id,
        label: `${s.type || 'Scan'}`,
        type: 'scan',
        val: 4,
        color: color,
        data: s,
      });
      links.push({ source: s.id, target: s.project_id, color: 'rgba(255,255,255,0.1)' });
    }
  });

  // NOTE: Vulnerabilities are NOT added as individual nodes anymore
  // This keeps the graph clean and focused on Projects → Scans structure

  return { nodes, links };
}

// -- Projects Table Data --

export interface ProjectTableRow {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived' | 'pending' | 'completed';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'safe';
  securityScore: number;
  trend: number[]; // Last 5 scores
  contributors: { name: string; color: string }[];
  lastScan: string;
  vulnerabilitiesCount: number;
}

export async function getProjectsTableData(): Promise<ProjectTableRow[]> {
  const supabase = createClient();

  // 1. Fetch Projects
  const { data: projects } = await supabase
    .from('projects')
    .select('*')
    .order('created_at', { ascending: false });
  if (!projects) return [];

  // 2. Fetch Latest Stats for each project
  // Ideally this is a join, but for MVP we fetch all latest scans
  const { data: latestScans } = await supabase
    .from('scans')
    .select('project_id, score, status, completed_at, findings_count')
    .order('completed_at', { ascending: false });

  // Process
  return projects.map((p) => {
    const pScans = latestScans?.filter((s) => s.project_id === p.id) || [];
    const latestScan = pScans[0];

    // Real Trend
    const currentScore = latestScan?.score;
    const trend = pScans.slice(0, 7).map((s) => s.score || 0);

    return {
      id: p.id,
      name: p.name,
      description: p.description,
      status: (p.status as any) || 'active',
      severity:
        latestScan?.score && latestScan.score < 50
          ? 'critical'
          : latestScan?.score && latestScan.score < 70
            ? 'high'
            : 'safe',
      securityScore: currentScore ?? 0,
      trend: trend,
      contributors: [], // TODO: Implement real contributors
      lastScan: latestScan?.completed_at || p.created_at,
      vulnerabilitiesCount: latestScan?.findings_count || 0,
    };
  });
}

// -- Advanced Dashboard Data --

export interface GlobalVuln {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'fixed';
  projectName: string;
  detectedAt: string;
  cveId?: string;
}

export async function getGlobalVulnerabilities(): Promise<GlobalVuln[]> {
  const supabase = createClient();

  // Fetch latest 10 open vulnerabilities across ALL projects
  const { data: vulns, error } = await supabase
    .from('vulnerabilities')
    .select(
      `
            id, title, severity, status, created_at, cve_id,
            projects (name)
        `
    )
    .eq('status', 'open')
    .order('created_at', { ascending: false })
    .limit(10);

  if (error) {
    logger.error('Error fetching global vulnerabilities:', { error });
    return [];
  }

  return vulns.map((v) => ({
    id: v.id,
    title: v.title,
    severity: v.severity as any,
    status: v.status as any,
    projectName: (v.projects as any)?.name || 'Unknown Project',
    detectedAt: v.created_at,
    cveId: v.cve_id || null,
  }));
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  status: 'online' | 'busy' | 'offline';
  lastActive: string;
}

export async function getTeamStats(): Promise<TeamMember[]> {
  const supabase = createClient();

  // Fetch profiles ordered by last seen
  const { data: profiles, error } = await supabase
    .from('profiles')
    .select('*')
    .order('last_seen_at', { ascending: false })
    .limit(5);

  if (error || !profiles) {
    return [];
  }

  const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);

  return profiles.map((p) => {
    const lastSeen = new Date(p.last_seen_at);
    const isOnline = lastSeen > fiveMinutesAgo;

    return {
      id: p.id,
      name: p.full_name || 'Team Member',
      role: p.role || 'Viewer',
      status: isOnline ? 'online' : 'offline',
      lastActive: formatDistanceToNow(lastSeen, { addSuffix: true }),
    };
  });
}

export interface AssetStat {
  type: string;
  count: number;
  riskLevel: number; // 0-100
}

export async function getAssetDistribution(): Promise<AssetStat[]> {
  const supabase = createClient();

  // Aggregate assets by type
  // Note: In a real production app, use a .rpc() call for aggregation to avoid fetching all rows
  const { data: assets, error } = await supabase.from('assets').select('type, risk_score');

  if (error || !assets || assets.length === 0) {
    return [];
  }

  const statsMap = assets.reduce(
    (acc, curr) => {
      if (!acc[curr.type]) {
        acc[curr.type] = { type: curr.type, count: 0, totalRisk: 0 };
      }
      acc[curr.type].count++;
      acc[curr.type].totalRisk += curr.risk_score || 0;
      return acc;
    },
    {} as Record<string, { type: string; count: number; totalRisk: number }>
  );

  return Object.values(statsMap).map((stat) => ({
    type: stat.type.charAt(0).toUpperCase() + stat.type.slice(1),
    count: stat.count,
    riskLevel: Math.min(100, Math.round(stat.totalRisk / stat.count)),
  }));
}

// -- Reports Page Data --

export interface ReportsGlobalStats {
  total_scans: number;
  total_projects: number;
  critical_count: number;
  high_count: number;
  avg_security_score: number;
}

export interface ReportProjectSummary {
  project_id: string;
  project_name: string;
  target_url: string;
  last_scan_date: string | null;
  last_scan_status: 'queued' | 'scanning' | 'completed' | 'failed' | null;
  critical_count: number;
  high_count: number;
  security_score: number;
}

export async function getReportsGlobalStats(): Promise<ReportsGlobalStats> {
  const supabase = createClient();

  // Get user's projects (RLS enforces ownership)
  const { data: projects } = await supabase.from('projects').select('id');
  const projectIds = projects?.map((p) => p.id) || [];

  if (projectIds.length === 0) {
    return {
      total_scans: 0,
      total_projects: 0,
      critical_count: 0,
      high_count: 0,
      avg_security_score: 0,
    };
  }

  // Get scans for user's projects
  const { data: scans, count: totalScans } = await supabase
    .from('scans')
    .select('id', { count: 'exact' })
    .in('project_id', projectIds);

  const scanIds = scans?.map((s) => s.id) || [];

  // Get findings by severity
  let criticalCount = 0;
  let highCount = 0;
  let mediumCount = 0;
  let lowCount = 0;

  if (scanIds.length > 0) {
    const { data: findings } = await supabase
      .from('findings')
      .select('severity')
      .in('scan_id', scanIds);

    findings?.forEach((f) => {
      if (f.severity === 'critical') criticalCount++;
      else if (f.severity === 'high') highCount++;
      else if (f.severity === 'medium') mediumCount++;
      else if (f.severity === 'low') lowCount++;
    });
  }

  // Calculate score using findings-based penalty formula
  const penalty = criticalCount * 15 + highCount * 8 + mediumCount * 3 + lowCount * 1;
  const avgScore = Math.max(0, Math.min(100, 100 - penalty));

  return {
    total_scans: totalScans || 0,
    total_projects: projectIds.length,
    critical_count: criticalCount,
    high_count: highCount,
    avg_security_score: avgScore,
  };
}

export async function getReportsProjects(): Promise<ReportProjectSummary[]> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc('get_project_scan_summaries');

  if (error) {
    logger.error('Error fetching project summaries:', { error });
    return [];
  }

  return data as ReportProjectSummary[];
}

export interface ReportDetails {
  id: string;
  created_at: string;
  target_url: string;
  project_name?: string;
  status: 'queued' | 'scanning' | 'completed' | 'failed';
  score: number;
  scan_duration_seconds?: number;
  severity_distribution?: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  vulnerability_types?: { name: string; count: number }[];
  findings: any[];
  assets: { count: number }[];
  completed_at?: string;
}

export async function getReportDetails(scanId: string): Promise<ReportDetails | null> {
  const supabase = createClient();
  console.log(`[getReportDetails] Fetching report via RPC for ID: ${scanId}`);

  const { data, error } = await supabase.rpc('get_scan_report', { scan_uuid: scanId });

  if (error) {
    logger.error(`[getReportDetails] RPC Error for ${scanId}:`, { error });
    return null;
  }

  if (!data) {
    console.warn(`[getReportDetails] No data returned for ID: ${scanId}`);
    return null;
  }

  // Transform RPC result to match expected interface
  const report: ReportDetails = {
    id: data.id,
    created_at: data.created_at,
    target_url: data.target_url,
    project_name: data.project_name,
    status: data.status,
    score: data.score,
    scan_duration_seconds: data.scan_duration_seconds,
    severity_distribution: data.severity_distribution,
    vulnerability_types: data.vulnerability_types,
    findings: data.findings || [],
    assets: [{ count: data.assets_count || 0 }],
    completed_at: data.completed_at,
  };

  console.log(
    `[getReportDetails] Success for ${scanId}. Findings: ${report.findings?.length}, Duration: ${report.scan_duration_seconds}s`
  );
  return report;
}

export interface ReportScanSummary {
  id: string;
  target_url: string;
  status: 'queued' | 'scanning' | 'completed' | 'failed';
  score: number;
  created_at: string;
  completed_at: string;
  project: { name: string };
  findings_count: number;
  high_severity_count: number;
}

export async function getReportsScans(): Promise<ReportScanSummary[]> {
  const supabase = createClient();
  console.log('[getReportsScans] Fetching recent scans via RPC...');

  const { data, error } = await supabase.rpc('get_recent_scans', { limit_count: 20 });

  if (error) {
    logger.error('[getReportsScans] Error fetching report scans:', { error });
    return [];
  }

  console.log(`[getReportsScans] Found ${data?.length} scans.`);

  return ((data as any[]) || []).map((s: any) => ({
    id: s.id,
    target_url: s.target_url,
    status: s.status,
    score: s.score,
    created_at: s.created_at,
    completed_at: s.completed_at,
    project: s.project,
    findings_count: s.findings_count,
    high_severity_count: s.high_severity_count,
  }));
}

export interface FindingDetails {
  id: string;
  scan_id: string;
  project_id: string;
  project_name: string;
  scan_created_at: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'fixed' | 'false_positive';
  remediation?: string;
  cve_id?: string;
  cwe_id?: string;
  cvss_score?: number;
  location?: string;
  evidence?: string;
  reference_links?: any[];
  affected_assets?: any[];
  created_at: string;
}

export async function getFindingDetails(findingId: string): Promise<FindingDetails | null> {
  const supabase = createClient();
  console.log(`[getFindingDetails] Fetching finding via RPC: ${findingId}`);

  const { data, error } = await supabase.rpc('get_finding_details', { finding_uuid: findingId });

  if (error) {
    logger.error(`[getFindingDetails] RPC Error for ${findingId}:`, { error });
    return null;
  }

  return data as FindingDetails;
}

// -- Project Details Page --

export interface ProjectTrend {
  date: string;
  score: number;
}

export async function getProjectRecentScans(projectId: string) {
  const supabase = createClient();
  // Fetch last 5 scans
  const { data: scans } = await supabase
    .from('scans')
    .select('*')
    .eq('project_id', projectId)
    .order('completed_at', { ascending: false })
    .limit(5);

  if (!scans || scans.length === 0) {
    return [];
  }

  return scans;
}

export async function getProjectTrend(projectId: string): Promise<ProjectTrend[]> {
  const supabase = createClient();
  // Fetch last 30 scans for this project
  const { data: scans } = await supabase
    .from('scans')
    .select('created_at, score')
    .eq('project_id', projectId)
    .eq('status', 'completed')
    .order('created_at', { ascending: true })
    .limit(30); // Last 30 scans

  if (!scans || scans.length === 0) {
    return [];
  }

  return scans.map((s) => ({
    date: new Date(s.created_at).toLocaleDateString(),
    score: s.score || 0,
  }));
}

export async function getProjectVulnerabilities(projectId: string): Promise<Vulnerability[]> {
  const supabase = createClient();

  // 1. Get scan IDs
  const { data: scans } = await supabase.from('scans').select('id').eq('project_id', projectId);
  const scanIds = scans?.map((s) => s.id) || [];

  if (scanIds.length === 0) return [];

  // 2. Get Vulns
  const { data, error } = await supabase
    .from('vulnerabilities')
    .select(
      `
            id, title, severity, status, created_at, scan_id
        `
    )
    .in('scan_id', scanIds)
    .eq('status', 'open')
    .order('created_at', { ascending: false });

  if (error) {
    logger.error('Error fetching project vulns:', { error });
    return [];
  }

  return (data || []).map((v: any) => ({
    id: v.id,
    title: v.title,
    severity: v.severity,
    status: v.status,
    project_id: projectId,
    created_at: v.created_at,
    location: 'Unknown',
  })) as Vulnerability[];
}

export async function getProjectDetails(projectId: string) {
  const supabase = createClient();
  const { data: project } = await supabase
    .from('projects')
    .select('*')
    .eq('id', projectId)
    .single();

  if (!project) return null;

  // Get latest scan
  const { data: latestScan } = await supabase
    .from('scans')
    .select('*')
    .eq('project_id', projectId)
    .order('created_at', { ascending: false })
    .limit(1)
    .single();

  // Get vulnerability counts
  // 1. Get all scan IDs for this project
  const { data: scans } = await supabase.from('scans').select('id').eq('project_id', projectId);
  const scanIds = scans?.map((s) => s.id) || [];

  let openIssues = { critical: 0, high: 0, medium: 0, low: 0, info: 0, total: 0 };

  if (scanIds.length > 0) {
    // 2. Aggregate open vulns
    const { data: vulns } = await supabase
      .from('vulnerabilities')
      .select('severity')
      .in('scan_id', scanIds)
      .eq('status', 'open');

    if (vulns) {
      vulns.forEach((v: any) => {
        const sev = v.severity?.toLowerCase() as keyof typeof openIssues;
        if (openIssues[sev] !== undefined) {
          openIssues[sev]++;
        }
        openIssues.total++;
      });
    }
  }

  return {
    ...project,
    lastScan: latestScan?.created_at,
    lastScanStatus: latestScan?.status,
    securityScore: latestScan?.score ?? null,
    targets: project.target_urls || [],
    stats: openIssues,
  };
}

// -- Projects Page Stats (For KPI Cards) --

export interface ProjectsPageStats {
  projectCount: number;
  projectCountChange: number; // Change since last period (e.g. last month)
  avgSecurityScore: number | null;
  criticalRisksCount: number;
  fixVelocity: 'High' | 'Medium' | 'Low' | null; // Calculated from avg time to fix
  avgTimeToFixDays: number | null;
}

export async function getProjectsPageStats(): Promise<ProjectsPageStats> {
  const supabase = createClient();

  // 1. Get user's projects (RLS enforces ownership)
  const { data: projects, count: projectCount } = await supabase
    .from('projects')
    .select('id', { count: 'exact' });

  const projectIds = projects?.map((p) => p.id) || [];

  // If no projects, return defaults
  if (projectIds.length === 0) {
    return {
      projectCount: 0,
      projectCountChange: 0,
      avgSecurityScore: null,
      criticalRisksCount: 0,
      fixVelocity: null,
      avgTimeToFixDays: null,
    };
  }

  // 2. Get ALL scans for user's projects
  const { data: scans } = await supabase
    .from('scans')
    .select('id, project_id, score, status')
    .in('project_id', projectIds)
    .order('created_at', { ascending: false });

  const scanIds = scans?.map((s) => s.id) || [];

  // 3. Get findings by severity to estimate score (same logic as Dashboard)
  let criticalCount = 0;
  let highCount = 0;
  let mediumCount = 0;
  let lowCount = 0;

  if (scanIds.length > 0) {
    const { data: findings } = await supabase
      .from('findings')
      .select('severity')
      .in('scan_id', scanIds);

    if (findings && findings.length > 0) {
      findings.forEach((f) => {
        if (f.severity === 'critical') criticalCount++;
        else if (f.severity === 'high') highCount++;
        else if (f.severity === 'medium') mediumCount++;
        else if (f.severity === 'low') lowCount++;
      });
    }
  }

  // Calculate security score using penalty formula
  // Critical: -15, High: -8, Medium: -3, Low: -1
  const penalty = criticalCount * 15 + highCount * 8 + mediumCount * 3 + lowCount * 1;
  const estimatedScore = Math.max(0, Math.min(100, 100 - penalty));

  // Use DB score if available and > 0, otherwise use estimated
  const dbScores = scans?.filter((s) => s.score && s.score > 0) || [];
  let avgScore = estimatedScore;
  if (dbScores.length > 0) {
    const total = dbScores.reduce((acc, curr) => acc + (curr.score || 0), 0);
    avgScore = Math.floor(total / dbScores.length);
  }

  // Critical risks = critical + high severity findings
  const criticalRisksCount = criticalCount + highCount;

  // 4. Calculate Fix Velocity based on estimated score (no minimum requirement)
  let fixVelocity: 'High' | 'Medium' | 'Low' | null = null;
  if (scanIds.length > 0) {
    if (avgScore >= 80) {
      fixVelocity = 'High';
    } else if (avgScore >= 50) {
      fixVelocity = 'Medium';
    } else {
      fixVelocity = 'Low';
    }
  }

  // 5. Calculate Avg Time to Fix from resolved findings
  let avgTimeToFixDays: number | null = null;
  if (scanIds.length > 0) {
    const { data: resolvedFindings } = await supabase
      .from('findings')
      .select('created_at, updated_at, status')
      .in('scan_id', scanIds)
      .eq('status', 'resolved');

    if (resolvedFindings && resolvedFindings.length > 0) {
      const totalDays = resolvedFindings.reduce((acc, f) => {
        const created = new Date(f.created_at).getTime();
        const resolved = new Date(f.updated_at).getTime(); // Use updated_at as resolve time
        const diffDays = (resolved - created) / (1000 * 60 * 60 * 24);
        return acc + diffDays;
      }, 0);
      avgTimeToFixDays = Math.round((totalDays / resolvedFindings.length) * 10) / 10; // 1 decimal
    }
  }

  return {
    projectCount: projectCount || 0,
    projectCountChange: 0, // Would require historical comparison
    avgSecurityScore: avgScore,
    criticalRisksCount: criticalRisksCount,
    fixVelocity: fixVelocity,
    avgTimeToFixDays: avgTimeToFixDays,
  };
}
