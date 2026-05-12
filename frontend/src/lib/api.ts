import { formatDistanceToNow } from 'date-fns';
import { api } from '@convex/_generated/api';
import type { Id } from '@convex/_generated/dataModel';
import { getConvexServerClient, safeConvex } from '@/lib/convex-server';

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived' | 'maintenance';
  target_urls: string[];
  item_count?: number;
}

export interface Scan {
  id: string;
  project_id: string;
  status: 'queued' | 'scanning' | 'processing' | 'paused' | 'completed' | 'failed' | 'cancelled';
  type: 'quick' | 'standard' | 'full' | 'deep' | 'credentialed';
  score: number;
  started_at: string;
  completed_at?: string;
}

export interface Vulnerability {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'fixed' | 'false_positive' | 'resolved' | 'ignored';
  project_id: string;
  created_at?: string;
  location?: string;
}

export interface ActivityLog {
  id: string;
  user_id: string;
  action_type: string;
  description: string;
  created_at: string;
  user_email?: string;
}

export interface SystemMetric {
  timestamp: string;
  traffic_in: number;
  traffic_out: number;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'root' | 'project' | 'scan' | 'vulnerability';
  val: number;
  color: string;
  data?: any;
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

export interface ProjectTableRow {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'archived' | 'pending' | 'completed';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'safe';
  securityScore: number;
  trend: number[];
  contributors: { name: string; color: string }[];
  lastScan: string;
  vulnerabilitiesCount: number;
}

export interface GlobalVuln {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'fixed';
  projectName: string;
  detectedAt: string;
  cveId?: string | null;
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  status: 'online' | 'busy' | 'offline';
  lastActive: string;
}

export interface AssetStat {
  type: string;
  count: number;
  riskLevel: number;
}

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

export interface FindingDetails {
  id: string;
  scan_id: string;
  project_id: string;
  project_name: string;
  scan_created_at: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'fixed' | 'false_positive' | 'resolved' | 'ignored';
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

export interface ProjectTrend {
  date: string;
  score: number;
}

export interface ProjectsPageStats {
  projectCount: number;
  projectCountChange: number;
  avgSecurityScore: number | null;
  criticalRisksCount: number;
  fixVelocity: 'High' | 'Medium' | 'Low' | null;
  avgTimeToFixDays: number | null;
}

export async function getDashboardStats() {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    return await client.query(api.dashboard.stats, {});
  }, {
    securityScore: 0,
    activeThreats: 0,
    completedScans: 0,
    availability: null,
  });
}

export async function getNetworkMetrics() {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const metrics = await client.query(api.dashboard.metrics, {});
    return metrics.map((metric: any) => ({
      created_at: new Date(metric.timestamp).toISOString(),
      traffic_in: metric.trafficInMbps ?? 0,
      traffic_out: metric.trafficOutMbps ?? 0,
    }));
  }, [] as any[]);
}

export async function getRecentActivity(): Promise<ActivityLog[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const logs = await client.query(api.dashboard.activity, {});
    return logs.map((log: any) => ({
      id: log._id,
      user_id: log.userId ?? 'system',
      action_type: log.actionType,
      description: log.description,
      created_at: new Date(log.createdAt).toISOString(),
      user_email: 'System',
      metadata: log.metadata,
    }));
  }, []);
}

export async function getDashboardProjects(): Promise<Project[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const projects = await client.query(api.projects.list, { status: 'active' });
    return projects.slice(0, 5).map(mapProject);
  }, []);
}

export async function getGraphData(): Promise<GraphData> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    return (await client.query(api.dashboard.graph, {})) as GraphData;
  }, { nodes: [], links: [] });
}

export async function getProjectsTableData(): Promise<ProjectTableRow[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const projects = await client.query(api.projects.listWithStats, {});
    return projects.map((project: any) => ({
      id: project.id,
      name: project.name,
      description: project.description,
      status: project.status,
      severity:
        project.securityScore !== null && project.securityScore < 50
          ? 'critical'
          : project.securityScore !== null && project.securityScore < 70
            ? 'high'
            : 'safe',
      securityScore: project.securityScore ?? 0,
      trend: project.trend ?? [],
      contributors: [],
      lastScan: new Date(project.lastScan ?? project.updatedAt).toISOString(),
      vulnerabilitiesCount: project.vulnerabilitiesCount ?? 0,
    }));
  }, []);
}

export async function getGlobalVulnerabilities(): Promise<GlobalVuln[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const findings = await client.query(api.findings.listOpen, { limit: 10 });
    return findings.map((finding: any) => ({
      id: finding.id,
      title: finding.title,
      severity: finding.severity,
      status: finding.status,
      projectName: finding.projectName,
      detectedAt: finding.detectedAt,
      cveId: finding.cveId ?? null,
    }));
  }, []);
}

export async function getTeamStats(): Promise<TeamMember[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const user = await client.query(api.users.me, {});
    if (!user) return [];
    return [
      {
        id: user._id,
        name: user.name ?? user.email ?? 'User',
        role: user.role ?? 'User',
        status: 'online',
        lastActive: formatDistanceToNow(new Date(user.updatedAt), { addSuffix: true }),
      },
    ];
  }, []);
}

export async function getAssetDistribution(): Promise<AssetStat[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    return await client.query(api.assets.distribution, {});
  }, []);
}

export async function getAssetInventory() {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    return await client.query(api.assets.inventory, {});
  }, { totalAssets: 0, domains: 0, subdomains: 0, ips: 0, assets: [] as any[] });
}

export async function getReportsGlobalStats(): Promise<ReportsGlobalStats> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    return await client.query(api.reports.globalStats, {});
  }, {
    total_scans: 0,
    total_projects: 0,
    critical_count: 0,
    high_count: 0,
    avg_security_score: 0,
  });
}

export async function getReportsProjects(): Promise<ReportProjectSummary[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const projects = await client.query(api.projects.listWithStats, {});
    return projects.map((project: any) => ({
      project_id: project.id,
      project_name: project.name,
      target_url: project.target_urls?.[0] ?? '',
      last_scan_date: project.lastScan ? new Date(project.lastScan).toISOString() : null,
      last_scan_status: project.lastScanStatus,
      critical_count: project.stats?.critical ?? 0,
      high_count: project.stats?.high ?? 0,
      security_score: project.securityScore ?? 0,
    }));
  }, []);
}

export async function getReportDetails(scanId: string): Promise<ReportDetails | null> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const report = await client.query(api.reports.scanReport, { scanId: scanId as Id<'scans'> });
    if (!report) return null;
    return {
      ...report,
      findings: (report.findings ?? []).map(mapFinding),
    } as ReportDetails;
  }, null);
}

export async function getReportsScans(): Promise<ReportScanSummary[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const scans = await client.query(api.reports.recentScans, { limit: 20 });
    return scans.map((scan: any) => ({
      id: scan._id,
      target_url: scan.target_url,
      status: scan.status,
      score: scan.score ?? 0,
      created_at: scan.created_at,
      completed_at: scan.completed_at,
      project: scan.project,
      findings_count: scan.findings_count ?? 0,
      high_severity_count: scan.high_severity_count ?? 0,
    }));
  }, []);
}

export async function getFindingDetails(findingId: string): Promise<FindingDetails | null> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const finding = await client.query(api.findings.get, { findingId: findingId as Id<'findings'> });
    return finding ? mapFinding(finding) : null;
  }, null);
}

export async function getRelatedFindings(
  scanId: string,
  title: string,
  severity: string
): Promise<FindingDetails[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const findings = await client.query(api.findings.related, {
      scanId: scanId as Id<'scans'>,
      title,
      severity,
    });
    return findings.map(mapFinding);
  }, []);
}

export async function getProjectRecentScans(projectId: string) {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const project = await client.query(api.projects.get, { projectId: projectId as Id<'projects'> });
    return (project?.scans ?? []).slice(0, 5).map(mapScan);
  }, []);
}

export async function getProjectTrend(projectId: string): Promise<ProjectTrend[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const project = await client.query(api.projects.get, { projectId: projectId as Id<'projects'> });
    return (project?.scans ?? [])
      .filter((scan: any) => scan.status === 'completed')
      .slice(0, 30)
      .reverse()
      .map((scan: any) => ({
        date: new Date(scan.createdAt).toLocaleDateString(),
        score: scan.score ?? 0,
      }));
  }, []);
}

export async function getProjectVulnerabilities(projectId: string): Promise<Vulnerability[]> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    return await client.query(api.findings.byProject, { projectId: projectId as Id<'projects'> });
  }, []);
}

export async function getProjectDetails(projectId: string) {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    return await client.query(api.projects.get, { projectId: projectId as Id<'projects'> });
  }, null);
}

export async function getProjectsPageStats(): Promise<ProjectsPageStats> {
  return safeConvex(async () => {
    const client = await getConvexServerClient();
    const [projects, reportStats] = await Promise.all([
      client.query(api.projects.listWithStats, {}),
      client.query(api.reports.globalStats, {}),
    ]);
    const scored = projects
      .map((project: any) => project.securityScore)
      .filter((score: any) => typeof score === 'number');
    const avgSecurityScore =
      scored.length > 0
        ? Math.round(scored.reduce((total: number, score: number) => total + score, 0) / scored.length)
        : reportStats.avg_security_score || null;
    const criticalRisksCount = reportStats.critical_count + reportStats.high_count;
    const fixVelocity =
      avgSecurityScore === null ? null : avgSecurityScore >= 80 ? 'High' : avgSecurityScore >= 50 ? 'Medium' : 'Low';

    return {
      projectCount: projects.length,
      projectCountChange: 0,
      avgSecurityScore,
      criticalRisksCount,
      fixVelocity,
      avgTimeToFixDays: null,
    };
  }, {
    projectCount: 0,
    projectCountChange: 0,
    avgSecurityScore: null,
    criticalRisksCount: 0,
    fixVelocity: null,
    avgTimeToFixDays: null,
  });
}

function mapProject(project: any): Project {
  return {
    id: project._id ?? project.id,
    name: project.name,
    description: project.description,
    status: project.status,
    target_urls: project.targetUrls ?? project.target_urls ?? [],
    item_count: project.targetUrls?.length ?? project.target_urls?.length ?? 0,
  };
}

function mapScan(scan: any) {
  return {
    ...scan,
    id: scan._id ?? scan.id,
    project_id: scan.projectId,
    target_url: scan.targetUrl,
    created_at: new Date(scan.createdAt).toISOString(),
    started_at: scan.startedAt ? new Date(scan.startedAt).toISOString() : new Date(scan.createdAt).toISOString(),
    completed_at: scan.completedAt ? new Date(scan.completedAt).toISOString() : null,
    score: scan.score ?? 0,
  };
}

function mapFinding(finding: any) {
  return {
    ...finding,
    id: finding._id ?? finding.id,
    scan_id: finding.scanId ?? finding.scan_id,
    project_id: finding.projectId ?? finding.project_id,
    project_name: finding.projectName ?? finding.project_name ?? 'Unknown Project',
    scan_created_at: finding.scanCreatedAt
      ? new Date(finding.scanCreatedAt).toISOString()
      : finding.scan_created_at ?? '',
    title: finding.title ?? 'Untitled finding',
    description: finding.description ?? '',
    cve_id: finding.cveId ?? finding.cve_id,
    cwe_id: finding.cweId ?? finding.cwe_id,
    cvss_score: finding.cvssScore ?? finding.cvss_score,
    reference_links: finding.referenceLinks ?? finding.reference_links,
    affected_assets: finding.affectedAssets ?? finding.affected_assets,
    created_at: finding.createdAt ? new Date(finding.createdAt).toISOString() : finding.created_at,
  };
}
