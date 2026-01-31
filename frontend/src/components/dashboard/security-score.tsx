'use client';

import { motion } from 'framer-motion';

import { EmptyState } from '@/components/ui/empty-state';

export function SecurityScoreGauge({ score }: { score: number | null }) {
  // Handle empty state
  if (score === null || score === undefined) {
    return (
      <div className="lg:row-span-2">
        <EmptyState
          icon="shield"
          title="Security Score Pending"
          message="Run your first scan to generate a security score."
          className="h-full border-none bg-white/[0.02]"
        />
      </div>
    );
  }

  // Calculate circumference for stroke-dasharray
  // r=95 -> C = 2 * pi * 95 ≈ 597
  const circumference = 597;
  const offset = circumference - (score / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="glass-card p-8 flex flex-col items-center justify-between lg:row-span-2 min-h-[400px] border border-white/5 bg-white/[0.02] backdrop-blur-xl rounded-[24px] shadow-2xl relative overflow-hidden group"
    >
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>

      <div className="w-full flex justify-between items-center mb-4 z-10">
        <h2 className="text-xs font-mono text-slate-400 uppercase tracking-widest">
          Global Security Score
        </h2>
        <span className="material-symbols-outlined text-slate-500 text-lg">verified_user</span>
      </div>

      <div className="relative w-56 h-56 flex items-center justify-center z-10">
        <svg className="w-full h-full -rotate-90 transform">
          <circle
            cx="112"
            cy="112"
            fill="none"
            r="95"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="14"
          ></circle>
          <motion.circle
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut', delay: 0.2 }}
            className="drop-shadow-[0_0_8px_rgba(16,185,129,0.4)]"
            cx="112"
            cy="112"
            fill="none"
            r="95"
            stroke="url(#scoreGradient)"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            strokeWidth="14"
          ></motion.circle>
          <defs>
            <linearGradient id="scoreGradient" x1="0%" x2="100%" y1="0%" y2="100%">
              <stop offset="0%" stopColor="#10B981"></stop>
              <stop offset="100%" stopColor="#34D399"></stop>
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute flex flex-col items-center">
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
            className="text-6xl font-bold text-white tracking-tighter"
          >
            {score}
          </motion.span>
        </div>
      </div>

      {/* Dynamic Status based on Score */}
      <div className="w-full space-y-4 mt-8 z-10">
        <div className="text-center text-xs text-slate-500 font-mono">
          {score >= 80
            ? '✓ Excellent Security'
            : score >= 50
              ? '⚠ Needs Improvement'
              : '⚡ Critical Issues Detected'}
        </div>
      </div>
    </motion.div>
  );
}
