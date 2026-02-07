import { createClient } from '@/utils/supabase/client';
import { formatDistanceToNow } from 'date-fns';

// -- Types --

export interface ActiveScanItem {
  id: string;
  target: string; // Mapped from target_url
  ip: string;
  type: 'cloud' | 'database' | 'web';
  node: string;
  status: string; // Mapped from current_action or status
  progress: number;
  started: string; // Mapped from started_at (relative)
  color: 'blue' | 'emerald' | 'orange';
}

export interface HistoryScanItem {
  id: string;
  name: string;
  target: string;
  completed: string;
  status: string;
  statusType: 'success' | 'danger' | 'warning';
  high: number;
  med: number;
  low: number;
}

// -- Fetchers --

export async function getActiveScans(): Promise<ActiveScanItem[]> {
  const supabase = createClient();
  const { data: scans, error } = await supabase
    .from('scans')
    .select('*')
    .in('status', ['queued', 'scanning', 'processing', 'paused']) // Include paused scans
    .order('created_at', { ascending: false });

  if (error || !scans) return [];

  return scans.map((s) => {
    // Heuristic mapping for UI color/icon logic based on target_url if explicit type missing?
    // Actually we added 'type' column in fix_scans_schema.sql.
    const type =
      s.type ||
      (s.target_url?.includes('db') ? 'database' : s.target_url?.includes('api') ? 'cloud' : 'web');
    const color = type === 'database' ? 'emerald' : type === 'cloud' ? 'blue' : 'orange';

    // Use real fields from DB (added in active_scans_migration.sql)
    const currentAction = s.current_action || (s.status ? s.status.toUpperCase() : 'UNKNOWN');
    const nodeName = s.node || 'Default-Worker';
    const progressVal = s.progress ?? 0; // handle null as 0

    // Use started_at if available, else created_at
    const startTime = s.started_at || s.created_at;

    return {
      id: s.id,
      target: s.target_url,
      ip: new URL(s.target_url).hostname || 'N/A',
      type,
      node: nodeName,
      status: currentAction,
      progress: progressVal,
      started: startTime
        ? formatDistanceToNow(new Date(startTime), { addSuffix: true })
        : 'Just now',
      color,
    };
  });
}

export async function getScanHistory(): Promise<HistoryScanItem[]> {
  const supabase = createClient();

  // Get completed/failed scans
  const { data: scans } = await supabase
    .from('scans')
    .select('id, status, target_url, completed_at, created_at')
    .in('status', ['completed', 'failed'])
    .order('created_at', { ascending: false })
    .limit(10);

  if (!scans || scans.length === 0) return [];

  // Get scan IDs to fetch findings
  const scanIds = scans.map((s) => s.id);

  // Fetch findings for these scans with severity
  const { data: findings } = await supabase
    .from('findings')
    .select('scan_id, severity')
    .in('scan_id', scanIds);

  // Group findings by scan_id and severity
  const findingsByScan = new Map<
    string,
    { critical: number; high: number; medium: number; low: number }
  >();

  findings?.forEach((f) => {
    if (!findingsByScan.has(f.scan_id)) {
      findingsByScan.set(f.scan_id, { critical: 0, high: 0, medium: 0, low: 0 });
    }
    const counts = findingsByScan.get(f.scan_id)!;
    if (f.severity === 'critical') counts.critical++;
    else if (f.severity === 'high') counts.high++;
    else if (f.severity === 'medium') counts.medium++;
    else if (f.severity === 'low') counts.low++;
  });

  return scans.map((s) => {
    const counts = findingsByScan.get(s.id) || { critical: 0, high: 0, medium: 0, low: 0 };
    const totalFindings = counts.critical + counts.high + counts.medium + counts.low;
    const isFailed = s.status === 'failed';
    const hasIssues = counts.critical > 0 || counts.high > 0;

    return {
      id: s.id,
      name: `Scan #${s.id.slice(0, 4)}`,
      target: s.target_url,
      completed: s.completed_at
        ? new Date(s.completed_at).toLocaleDateString()
        : s.created_at
          ? new Date(s.created_at).toLocaleDateString()
          : 'Unknown',
      status: isFailed
        ? 'Failed'
        : hasIssues
          ? 'Issues Found'
          : totalFindings > 0
            ? 'Low Risk'
            : 'Clean',
      statusType: isFailed
        ? 'danger'
        : hasIssues
          ? 'danger'
          : totalFindings > 0
            ? 'warning'
            : 'success',
      high: counts.critical + counts.high, // Combined critical+high as "High"
      med: counts.medium,
      low: counts.low,
    };
  });
}

export async function getScanStats() {
  const supabase = createClient();

  // Calculate start of current month for filtering
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();

  const [{ count: monthTotal }, { count: completed }] = await Promise.all([
    // Filter by current month
    supabase
      .from('scans')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', startOfMonth),
    supabase
      .from('scans')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'completed')
      .gte('created_at', startOfMonth),
  ]);

  const successRate = monthTotal ? Math.round(((completed || 0) / monthTotal) * 100) : 100;

  // Calculate Average Duration
  const { data: durationData } = await supabase
    .from('scans')
    .select('created_at, completed_at')
    .eq('status', 'completed')
    .not('completed_at', 'is', null)
    .limit(50);

  let avgDuration = 'N/A';
  if (durationData && durationData.length > 0) {
    const totalSeconds = durationData.reduce((acc, s) => {
      const start = new Date(s.created_at).getTime();
      const end = new Date(s.completed_at).getTime();
      return acc + (end - start) / 1000;
    }, 0);
    const avgSeconds = Math.round(totalSeconds / durationData.length);
    if (avgSeconds < 60) {
      avgDuration = `${avgSeconds}s`;
    } else {
      avgDuration = `${Math.floor(avgSeconds / 60)}m ${avgSeconds % 60}s`;
    }
  }

  return {
    monthCount: monthTotal || 0,
    avgDuration,
    successRate: `${successRate}%`,
  };
}

// -- Scan Control API --

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

export async function pauseScan(scanId: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_URL}/scans/${scanId}/pause`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
  });
  return response.json();
}

export async function resumeScan(scanId: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_URL}/scans/${scanId}/resume`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
  });
  return response.json();
}

export async function cancelScan(scanId: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_URL}/scans/${scanId}/cancel`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
  });
  return response.json();
}
