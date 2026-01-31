'use client';

import { motion } from 'framer-motion';
import { Shield, ExternalLink, Calendar, AlertCircle, FileText } from 'lucide-react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

interface ScanSummary {
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

interface ScansListProps {
  scans: ScanSummary[];
}

export function ScansList({ scans }: ScansListProps) {
  if (!scans || scans.length === 0) {
    return (
      <div className="glass-panel p-10 text-center rounded-[24px]">
        <p className="text-slate-400">No completed scans found.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {scans.map((scan, idx) => (
        <motion.div
          key={scan.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05 }}
          className="glass-panel p-6 rounded-[24px] group hover:bg-white/[0.08] transition-all relative overflow-hidden flex flex-col h-full"
        >
          {/* Header */}
          <div className="flex justify-between items-start mb-4 relative z-10">
            <div>
              <div className="text-xs font-mono text-slate-500 mb-1">{scan.project.name}</div>
              <h3
                className="text-lg font-bold text-white truncate max-w-[200px]"
                title={scan.target_url}
              >
                {scan.target_url}
              </h3>
            </div>
            <div
              className={`
                flex items-center justify-center w-10 h-10 rounded-full font-bold text-sm
                ${
                  scan.score >= 80
                    ? 'bg-emerald-500/20 text-emerald-500'
                    : scan.score >= 50
                      ? 'bg-amber-500/20 text-amber-500'
                      : 'bg-rose-500/20 text-rose-500'
                }
            `}
            >
              {scan.score}
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm text-slate-400 mb-6 flex-grow">
            <div className="flex items-center gap-1.5" title="Total Findings">
              <Shield className="h-4 w-4" />
              <span>{scan.findings_count}</span>
            </div>
            <div className="flex items-center gap-1.5 text-rose-400" title="High Severity">
              <AlertCircle className="h-4 w-4" />
              <span>{scan.high_severity_count}</span>
            </div>
            <div className="flex items-center gap-1.5" title="Completed">
              <Calendar className="h-4 w-4" />
              <span>{formatDistanceToNow(new Date(scan.completed_at), { addSuffix: true })}</span>
            </div>
          </div>

          <div className="mt-auto pt-4 border-t border-white/5 flex justify-between items-center">
            <Link
              href={`/reports/${scan.id}`}
              className="text-blue-400 hover:text-blue-300 text-sm font-bold flex items-center group/link"
            >
              View Report{' '}
              <ExternalLink className="ml-1 h-3 w-3 group-hover/link:translate-x-1 transition-transform" />
            </Link>
            <span className="text-xs uppercase font-bold text-emerald-500 bg-emerald-900/20 px-2 py-0.5 rounded">
              Completed
            </span>
          </div>

          {/* Background Gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </motion.div>
      ))}
    </div>
  );
}
