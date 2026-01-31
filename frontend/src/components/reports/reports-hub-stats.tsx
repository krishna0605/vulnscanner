'use client';

import { motion } from 'framer-motion';
import { ShieldCheck, Activity, AlertTriangle, Layers } from 'lucide-react';
import { ReportsGlobalStats } from '@/lib/api';

interface ReportsHubStatsProps {
  stats: ReportsGlobalStats;
}

export function ReportsHubStats({ stats }: ReportsHubStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
      {/* Card 1: Total Scans */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-panel p-6 rounded-[20px] relative overflow-hidden group border border-white/5 hover:border-white/10 transition-colors"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-3 bg-blue-500/10 rounded-xl relative z-10">
            <Activity className="h-6 w-6 text-blue-400" />
          </div>
          {/* Badge removed - would require historical data to calculate */}
        </div>
        <div className="relative z-10">
          <h3 className="text-3xl font-bold text-white mb-1">{stats.total_scans}</h3>
          <p className="text-slate-400 text-sm font-medium">Total Scans Performed</p>
        </div>
      </motion.div>

      {/* Card 2: Active Projects */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-panel p-6 rounded-[20px] relative overflow-hidden group border border-white/5 hover:border-white/10 transition-colors"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-3 bg-violet-500/10 rounded-xl relative z-10">
            <Layers className="h-6 w-6 text-violet-400" />
          </div>
        </div>
        <div className="relative z-10">
          <h3 className="text-3xl font-bold text-white mb-1">{stats.total_projects}</h3>
          <p className="text-slate-400 text-sm font-medium">Active Projects</p>
        </div>
      </motion.div>

      {/* Card 3: Critical Issues */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-panel p-6 rounded-[20px] relative overflow-hidden group border border-white/5 hover:border-white/10 transition-colors"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-3 bg-red-500/10 rounded-xl relative z-10">
            <AlertTriangle className="h-6 w-6 text-red-400" />
          </div>
          <span className="text-xs font-semibold px-2 py-1 rounded-lg bg-red-500/10 text-red-400 border border-red-500/10">
            Action Req.
          </span>
        </div>
        <div className="relative z-10">
          <h3 className="text-3xl font-bold text-white mb-1">{stats.critical_count}</h3>
          <p className="text-slate-400 text-sm font-medium">Critical Issues</p>
        </div>
      </motion.div>

      {/* Card 4: Avg Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-panel p-6 rounded-[20px] relative overflow-hidden group border border-white/5 hover:border-white/10 transition-colors"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-3 bg-emerald-500/10 rounded-xl relative z-10">
            <ShieldCheck className="h-6 w-6 text-emerald-400" />
          </div>
        </div>
        <div className="relative z-10">
          <h3 className="text-3xl font-bold text-white mb-1">{stats.avg_security_score}%</h3>
          <p className="text-slate-400 text-sm font-medium">Avg Security Score</p>
        </div>

        {/* Visual Progress Bar for Score */}
        <div className="mt-4 h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500 rounded-full"
            style={{ width: `${stats.avg_security_score}%` }}
          ></div>
        </div>
      </motion.div>
    </div>
  );
}
