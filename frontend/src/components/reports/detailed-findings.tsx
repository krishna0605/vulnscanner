'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

interface DetailedFindingsProps {
  findings: any[];
  scanId: string;
}

export function DetailedFindings({ findings = [], scanId }: DetailedFindingsProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-rose-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-slate-500'; // Info
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'fixed':
      case 'patched':
        return 'text-emerald-500 bg-emerald-900/30 border-emerald-500/20';
      case 'false_positive':
        return 'text-slate-500 bg-slate-900/30 border-slate-500/20';
      default:
        return 'text-amber-500 bg-amber-900/30 border-amber-500/20'; // Open/New
    }
  };

  return (
    <div className="mt-4">
      <h2 className="text-2xl font-bold text-white mb-6">Detailed Findings</h2>
      {findings.length === 0 ? (
        <div className="text-slate-400 italic">No findings reported for this scan.</div>
      ) : (
        <div className="space-y-6">
          {findings.map((finding, idx) => {
            const severityColor = getSeverityColor(finding.severity || 'info');
            const statusColor = getStatusColor(finding.status || 'open');
            const isCritical = finding.severity === 'critical';
            const isHigh = finding.severity === 'high';

            return (
              <motion.div
                key={finding.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + idx * 0.1 }}
                className="glass-panel p-8 rounded-[24px] hover:bg-white/[0.08] transition-all duration-300 group cursor-default relative overflow-hidden"
              >
                {/* Status Strip */}
                <div
                  className={`absolute left-0 top-0 bottom-0 w-1 ${severityColor} opacity-0 group-hover:opacity-100 transition-opacity`}
                ></div>

                <div className="flex flex-col md:flex-row md:items-start justify-between mb-4 gap-4">
                  <div>
                    <h3 className="text-xl font-bold text-white mb-3 group-hover:text-cyan-400 transition-colors">
                      {finding.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-3 text-sm">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${isCritical ? 'bg-rose-500/10 text-rose-500 border-rose-500/20' : isHigh ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' : 'bg-slate-500/10 text-slate-300 border-slate-500/20'}`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${severityColor} mr-2`}></span>{' '}
                        {finding.severity}
                      </span>
                      {finding.cve_id && (
                        <span className="text-slate-500 font-mono"># {finding.cve_id}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium border ${statusColor}`}
                    >
                      {finding.status}
                    </span>
                    <Link
                      href={`/reports/${scanId}/findings/${finding.id}`}
                      className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/20 transition-all hover:scale-105"
                    >
                      View Details{' '}
                      <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
                    </Link>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/5 mt-4 group-hover:border-white/10 transition-colors">
                  <h4 className="text-sky-400 font-medium text-sm mb-2 flex items-center gap-2">
                    Description & Remediation
                  </h4>
                  <p className="text-slate-400 text-sm leading-relaxed max-w-4xl">
                    {finding.description}
                    {finding.remediation && (
                      <>
                        <br />
                        <br />
                        <strong>Fix:</strong> {finding.remediation}
                      </>
                    )}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
