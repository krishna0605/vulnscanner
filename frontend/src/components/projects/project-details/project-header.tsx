'use client';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface ProjectHeaderProps {
  project: any;
}

export function ProjectHeader({ project }: ProjectHeaderProps) {
  return (
    <div className="glass-panel p-6 lg:p-8 rounded-[24px] relative overflow-hidden group">
      <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
        <div>
          <div className="flex items-center gap-4 mb-2">
            <h1 className="text-3xl lg:text-4xl font-bold text-white tracking-tight">
              Project: {project.name}
            </h1>
            <span
              className={`px-3 py-1 rounded-full border text-xs font-bold tracking-wide uppercase shadow-[0_0_10px_rgba(16,185,129,0.2)] ${
                project.status === 'active'
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                  : 'bg-slate-500/10 border-slate-500/20 text-slate-400'
              }`}
            >
              {project.status || 'Active Monitoring'}
            </span>
          </div>

          <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm text-slate-400 font-mono mt-2">
            <span className="flex items-center">
              <span className="material-symbols-outlined text-base mr-2">fingerprint</span> ID:{' '}
              {project.id.slice(0, 8).toUpperCase()}
            </span>
            <span className="flex items-center">
              <span className="material-symbols-outlined text-base mr-2">language</span> Target:{' '}
              {project.targets?.[0] || 'app.prometheus-x.io'}
            </span>
            <span className="flex items-center">
              <span className="material-symbols-outlined text-base mr-2">calendar_today</span> Last
              Scan:{' '}
              {project.lastScan
                ? formatDistanceToNow(new Date(project.lastScan), { addSuffix: true })
                : 'Never'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-8 w-full lg:w-auto bg-black/20 p-4 rounded-2xl border border-white/5 backdrop-blur-sm">
          <div className="flex flex-col">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Security Health
            </span>
            <div className="flex items-baseline mt-1">
              <span
                className={`text-3xl font-bold text-glow ${
                  project.securityScore >= 80 ? 'text-white' : 'text-white' // Reference uses white for score, colored dot usually
                }`}
              >
                {project.securityScore}
              </span>
              <span className="text-sm text-slate-500 ml-1">/100</span>
            </div>
          </div>

          <div className="h-10 w-px bg-white/10"></div>

          <div className="flex flex-col">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Open Issues
            </span>
            <div className="flex items-baseline mt-1 space-x-3">
              <span className="text-white font-mono font-bold flex items-center">
                <span className="w-2 h-2 rounded-full bg-red-500 mr-2 shadow-glow-red"></span>
                {project.stats?.critical || 0}
              </span>
              <span className="text-white font-mono font-bold flex items-center">
                <span className="w-2 h-2 rounded-full bg-orange-500 mr-2 shadow-glow-orange"></span>
                {project.stats?.high || 0}
              </span>
              <span className="text-white font-mono font-bold flex items-center">
                <span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>
                {project.stats?.medium || 0}
              </span>
            </div>
          </div>

          <Button
            className="ml-auto lg:ml-4 p-3 bg-white text-black rounded-xl hover:bg-slate-200 transition-colors shadow-glow hover:shadow-glow-hover group h-auto w-auto min-w-0"
            size="icon"
          >
            <RefreshCw className="h-5 w-5 group-hover:animate-spin" />
          </Button>
        </div>
      </div>
    </div>
  );
}
