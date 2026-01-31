'use client';

import { ReportStats } from '@/components/reports/report-stats';
import { ReportVisualizations } from '@/components/reports/report-charts';
import { DetailedFindings } from '@/components/reports/detailed-findings';
import { FileText, Download, ArrowLeft, Calendar } from 'lucide-react';
import Link from 'next/link';
import { formatDistance } from 'date-fns';
import { downloadCSV, printAsPDF, formatDuration } from '@/utils/export-utils';
import type { ReportDetails } from '@/lib/api';

interface ReportPageClientProps {
  report: ReportDetails;
  scanId: string;
}

export function ReportPageClient({ report, scanId }: ReportPageClientProps) {
  // Calculate Metrics from enhanced data
  const findings = report.findings || [];
  const totalVulns = findings.length;

  // Use severity_distribution from RPC if available, otherwise calculate from findings
  const severityDist =
    report.severity_distribution ||
    findings.reduce(
      (acc, f) => {
        const sev = (f.severity || 'info').toLowerCase();
        acc[sev] = (acc[sev] || 0) + 1;
        return acc;
      },
      { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
    );

  const highSeverityCount = severityDist.critical + severityDist.high;

  // Use scan_duration_seconds from RPC if available
  let durationString = 'N/A';
  if (report.scan_duration_seconds) {
    durationString = formatDuration(report.scan_duration_seconds);
  } else if (report.created_at && report.completed_at) {
    const start = new Date(report.created_at);
    const end = new Date(report.completed_at);
    durationString = formatDistance(start, end, { includeSeconds: true });
  } else if (report.status === 'scanning') {
    durationString = 'In Progress';
  }

  // Format scan date for display
  const scanDate = report.created_at
    ? new Date(report.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'Unknown';

  const handleExportCSV = () => {
    downloadCSV({
      id: report.id,
      target_url: report.target_url,
      project_name: report.project_name,
      created_at: report.created_at,
      completed_at: report.completed_at,
      scan_duration_seconds: report.scan_duration_seconds,
      severity_distribution: severityDist,
      findings: findings,
    });
  };

  const handleExportPDF = () => {
    printAsPDF();
  };

  return (
    <div className="max-w-[1600px] mx-auto animate-in fade-in duration-700 print:bg-white print:text-black">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-sm text-slate-400 mb-6 print:hidden">
        <Link href="/projects" className="hover:text-white transition-colors">
          Projects
        </Link>
        <span>/</span>
        {report.project_name && (
          <>
            <span className="text-slate-300">{report.project_name}</span>
            <span>/</span>
          </>
        )}
        <span className="text-cyan-400">Reports</span>
      </div>

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-6">
        <div>
          <h1 className="text-4xl font-bold text-white tracking-tight mb-2 print:text-black">
            Scan Report:{' '}
            <span className="text-cyan-400 print:text-gray-700">{report.target_url}</span>
          </h1>
          <div className="flex items-center gap-2 text-slate-400 print:text-gray-600">
            <Calendar className="h-4 w-4" />
            <span>Scanned on {scanDate}</span>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex space-x-4 print:hidden">
          <button
            onClick={handleExportCSV}
            className="px-5 py-2.5 rounded-lg border border-white/20 text-white text-sm font-medium hover:bg-white/5 transition-all flex items-center group"
          >
            <FileText className="mr-2 h-5 w-5 text-slate-400 group-hover:text-white transition-colors" />
            Export as CSV
          </button>
          <button
            onClick={handleExportPDF}
            className="px-5 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-sm font-bold shadow-[0_0_15px_rgba(2,132,199,0.3)] hover:shadow-[0_0_25px_rgba(2,132,199,0.5)] transition-all flex items-center"
          >
            <Download className="mr-2 h-5 w-5" />
            Export as PDF
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <ReportStats
        totalVulnerabilities={totalVulns}
        highSeverityCount={highSeverityCount}
        durationString={durationString}
      />

      {/* Charts - pass enhanced data */}
      <ReportVisualizations
        findings={findings}
        severityDistribution={severityDist}
        vulnerabilityTypes={report.vulnerability_types}
      />

      {/* Findings List */}
      <DetailedFindings findings={findings} scanId={scanId} />

      {/* Back Link (mobile + print hidden) */}
      <div className="mt-10 print:hidden">
        <Link
          href="/reports"
          className="inline-flex items-center text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Reports Hub
        </Link>
      </div>
    </div>
  );
}
