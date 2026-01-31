/**
 * Export utilities for generating CSV and PDF reports
 */

export interface Finding {
  id: string;
  title: string;
  description?: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  status: 'open' | 'fixed' | 'false_positive';
  category?: string;
  cve_id?: string;
  cvss_score?: number;
  remediation?: string;
}

export interface ReportData {
  id: string;
  target_url: string;
  project_name?: string;
  created_at: string;
  completed_at?: string;
  scan_duration_seconds?: number;
  severity_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  findings: Finding[];
}

/**
 * Generate CSV content from findings
 */
export function generateCSV(reportData: ReportData): string {
  const headers = [
    'ID',
    'Title',
    'Severity',
    'Status',
    'Category',
    'CVE ID',
    'CVSS Score',
    'Description',
    'Remediation',
  ];

  const rows = reportData.findings.map((f) => [
    f.id,
    `"${(f.title || '').replace(/"/g, '""')}"`,
    f.severity,
    f.status,
    f.category || 'N/A',
    f.cve_id || 'N/A',
    f.cvss_score?.toString() || 'N/A',
    `"${(f.description || '').replace(/"/g, '""').replace(/\n/g, ' ')}"`,
    `"${(f.remediation || '').replace(/"/g, '""').replace(/\n/g, ' ')}"`,
  ]);

  // Add summary section at top
  const summary = [
    ['Scan Report Summary'],
    ['Target URL', reportData.target_url],
    ['Project', reportData.project_name || 'N/A'],
    ['Scan Date', new Date(reportData.created_at).toLocaleString()],
    ['Total Findings', reportData.findings.length.toString()],
    ['Critical', reportData.severity_distribution.critical.toString()],
    ['High', reportData.severity_distribution.high.toString()],
    ['Medium', reportData.severity_distribution.medium.toString()],
    ['Low', reportData.severity_distribution.low.toString()],
    [''],
    ['Detailed Findings'],
    headers,
  ];

  const allRows = [...summary, ...rows];
  return allRows.map((row) => row.join(',')).join('\n');
}

/**
 * Download CSV file
 */
export function downloadCSV(reportData: ReportData, filename?: string): void {
  const csvContent = generateCSV(reportData);
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || `scan-report-${reportData.id}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Generate PDF using browser print functionality
 * Opens a print dialog with the current page styled for printing
 */
export function printAsPDF(): void {
  window.print();
}

/**
 * Format duration in seconds to human readable string (e.g., "2h 15m")
 */
export function formatDuration(seconds: number): string {
  if (!seconds || seconds <= 0) return 'N/A';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}
