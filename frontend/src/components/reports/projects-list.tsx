'use client';

import { motion } from 'framer-motion';
import {
  ArrowRight,
  Shield,
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { ReportProjectSummary } from '@/lib/api';

interface ProjectsListProps {
  projects: ReportProjectSummary[];
}

export function ProjectsList({ projects }: ProjectsListProps) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-400';
    if (score >= 70) return 'text-blue-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const getStatusIcon = (status: string | null) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-emerald-400" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-400" />;
      case 'scanning':
        return <Clock className="h-4 w-4 text-blue-400 animate-pulse" />;
      case 'queued':
        return <Clock className="h-4 w-4 text-slate-400" />;
      default:
        return <Clock className="h-4 w-4 text-slate-500" />;
    }
  };

  return (
    <div className="glass-panel rounded-[20px] overflow-hidden border border-white/5">
      <div className="p-6 border-b border-white/5 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Project Reports</h2>
          <p className="text-slate-400 text-sm">Latest security assessments for your projects</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5 bg-white/[0.02]">
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Project
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Last Scan
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Vulnerabilities
              </th>
              <th className="px-6 py-4 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Score
              </th>
              <th className="px-6 py-4 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {projects.map((project, index) => (
              <motion.tr
                key={project.project_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="group hover:bg-white/[0.02] transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20 mr-4">
                      <Shield className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white group-hover:text-blue-400 transition-colors">
                        {project.project_name}
                      </div>
                      <div className="text-xs text-slate-500">{project.target_url}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-slate-300">
                    {project.last_scan_date
                      ? formatDistanceToNow(new Date(project.last_scan_date), { addSuffix: true })
                      : 'Never scanned'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(project.last_scan_status)}
                    <span className="text-sm text-slate-300 capitalize">
                      {project.last_scan_status || 'Pending'}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-red-500/10 border border-red-500/10">
                      <ShieldAlert className="h-3 w-3 text-red-400" />
                      <span className="text-xs font-bold text-red-400">
                        {project.critical_count}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-orange-500/10 border border-orange-500/10">
                      <AlertTriangle className="h-3 w-3 text-orange-400" />
                      <span className="text-xs font-bold text-orange-400">
                        {project.high_count}
                      </span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`text-lg font-bold ${getScoreColor(project.security_score)}`}>
                    {project.security_score}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link
                    href={`/reports/${project.last_scan_date ? encodeURIComponent(project.project_name + '-' + new Date(project.last_scan_date).getTime()) : 'latest'}`}
                    className="inline-flex items-center px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white transition-colors group-hover:bg-blue-600 group-hover:shadow-[0_0_15px_rgba(37,99,235,0.4)]"
                  >
                    View Report
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </td>
              </motion.tr>
            ))}

            {projects.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                  No projects found. Start a scan to see reports here.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
