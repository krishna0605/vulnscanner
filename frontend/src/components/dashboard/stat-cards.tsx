'use client';

import { motion } from 'framer-motion';

interface CardProps {
  count?: number;
  score?: number;
}

export function ActiveThreatCard({ count = 0 }: CardProps) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="glass-card p-6 flex flex-col justify-between group overflow-hidden relative border border-white/5 bg-white/[0.02] backdrop-blur-xl rounded-[24px]"
    >
      <div className="flex justify-between items-start z-10">
        <h3 className="text-xs font-mono text-slate-400 uppercase tracking-widest">
          Active Threat
        </h3>
        <span className="material-symbols-outlined text-amber-500">warning</span>
      </div>

      <div className="mt-4 z-10">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.5)] animate-pulse"></div>
          <span className="text-3xl font-bold text-white tracking-tight">
            {count > 0 ? `${count} ISSUES` : 'LOW RISK'}
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-3 font-light leading-relaxed">
          {count > 0
            ? 'Critical findings require attention.'
            : 'System identified unusual scanning patterns from external EU subnets.'}
        </p>
      </div>

      {/* Decorative Blur */}
      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-amber-500/10 blur-[40px] rounded-full group-hover:bg-amber-500/20 transition-all duration-500"></div>
    </motion.div>
  );
}

export function CurrentScansCard({ count = 0 }: CardProps) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="glass-card p-6 flex flex-col justify-between group overflow-hidden relative border border-white/5 bg-white/[0.02] backdrop-blur-xl rounded-[24px]"
    >
      <div className="flex justify-between items-start z-10">
        <h3 className="text-xs font-mono text-slate-400 uppercase tracking-widest">
          Completed Scans
        </h3>
        <span className="material-symbols-outlined text-emerald-500">check_circle</span>
      </div>

      <div className="mt-4 z-10">
        <div className="flex items-end gap-2">
          <span className="text-4xl font-bold text-white tracking-tighter">{count}</span>
          <span className="text-xs text-slate-500 mb-1.5 font-mono">scans</span>
        </div>
        <p className="text-xs text-slate-500 mt-3 font-light">
          {count === 0
            ? 'No scans completed yet'
            : `${count} security scan${count > 1 ? 's' : ''} completed`}
        </p>
      </div>

      {/* Decorative Blur */}
      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-emerald-500/10 blur-[40px] rounded-full group-hover:bg-emerald-500/20 transition-all duration-500"></div>
    </motion.div>
  );
}

import { EmptyState } from '@/components/ui/empty-state';

export function AvailabilityCard({ score }: { score: number | null }) {
  if (score === null || score === undefined) {
    return (
      <motion.div
        whileHover={{ y: -5 }}
        className="glass-card flex flex-col justify-between group overflow-hidden relative border border-white/5 bg-white/[0.02] backdrop-blur-xl rounded-[24px]"
      >
        <EmptyState
          icon="cloud_off"
          title="Availability"
          message="No metric data available."
          className="border-none bg-transparent"
        />
      </motion.div>
    );
  }

  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="glass-card p-6 flex flex-col justify-between group overflow-hidden relative border border-white/5 bg-white/[0.02] backdrop-blur-xl rounded-[24px]"
    >
      <div className="flex justify-between items-start z-10">
        <h3 className="text-xs font-mono text-slate-400 uppercase tracking-widest">Availability</h3>
        <span className="material-symbols-outlined text-emerald-400">check_circle</span>
      </div>
      <div className="mt-4 z-10">
        <div className="flex items-end gap-2">
          <span className="text-4xl font-bold text-white tracking-tighter">{score}%</span>
        </div>
        <div className="flex gap-1.5 mt-4 h-6">
          {[...Array(7)].map((_, i) => (
            <div
              key={i}
              className={`flex-1 rounded-sm ${i === 5 && score < 99 ? 'bg-amber-500/20 border border-amber-500/30' : 'bg-emerald-500/20 border border-emerald-500/30'}`}
            ></div>
          ))}
        </div>
      </div>
      {/* Decorative Blur */}
      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-emerald-500/10 blur-[40px] rounded-full group-hover:bg-emerald-500/20 transition-all duration-500"></div>
    </motion.div>
  );
}
