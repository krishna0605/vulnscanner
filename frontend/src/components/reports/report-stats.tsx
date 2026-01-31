'use client';
import { motion } from 'framer-motion';
import { ShieldAlert, Zap, Clock } from 'lucide-react';

interface ReportStatsProps {
  totalVulnerabilities: number;
  highSeverityCount: number;
  durationString: string;
}

export function ReportStats({
  totalVulnerabilities,
  highSeverityCount,
  durationString,
}: ReportStatsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-panel p-8 rounded-[24px] relative overflow-hidden group"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <p className="text-slate-400 text-sm font-medium mb-3 relative z-10">
          Total Vulnerabilities
        </p>
        <h3 className="text-5xl font-bold text-white tracking-tight relative z-10">
          {totalVulnerabilities}
        </h3>
        <ShieldAlert className="absolute top-8 right-8 h-12 w-12 text-white/5 group-hover:text-white/10 transition-colors" />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-panel p-8 rounded-[24px] relative overflow-hidden group"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div className="absolute -right-10 -top-10 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl group-hover:bg-orange-500/20 transition-all"></div>
        <p className="text-slate-400 text-sm font-medium mb-3 relative z-10">High Severity</p>
        <h3 className="text-5xl font-bold text-orange-500 tracking-tight relative z-10">
          {highSeverityCount}
        </h3>
        <Zap className="absolute top-8 right-8 h-12 w-12 text-orange-500/10 group-hover:text-orange-500/20 transition-colors" />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-panel p-8 rounded-[24px] relative overflow-hidden group"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <p className="text-slate-400 text-sm font-medium mb-3 relative z-10">Scan Duration</p>
        <h3 className="text-5xl font-bold text-white tracking-tight relative z-10">
          {durationString}
        </h3>
        <Clock className="absolute top-8 right-8 h-12 w-12 text-blue-500/10 group-hover:text-blue-500/20 transition-colors" />
      </motion.div>
    </div>
  );
}
