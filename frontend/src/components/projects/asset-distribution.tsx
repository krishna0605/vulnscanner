'use client';

import { AssetStat } from '@/lib/api';
import { GlassCard } from './motion-wrapper';
import { motion } from 'framer-motion';

export function AssetDistributionCard({ stats }: { stats: AssetStat[] }) {
  return (
    <GlassCard className="p-6 h-[350px] flex flex-col relative overflow-hidden">
      <h3 className="text-white font-bold text-lg mb-6 flex items-center gap-2">
        <span className="material-symbols-outlined text-purple-400">dns</span>
        Attack Surface
      </h3>

      <div className="flex-1 space-y-5">
        {stats.map((stat, i) => (
          <div key={i} className="group">
            <div className="flex justify-between items-end mb-2">
              <span className="text-sm text-slate-300 font-medium">{stat.type}</span>
              <span className="text-xs font-mono text-slate-400">{stat.count} Assets</span>
            </div>
            {/* Progress Bar Container */}
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden relative">
              {/* Fill */}
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${stat.riskLevel}%` }}
                transition={{ duration: 1, delay: 0.5 + i * 0.1, ease: 'easeOut' }}
                className={`h-full rounded-full ${
                  stat.riskLevel > 80
                    ? 'bg-red-500'
                    : stat.riskLevel > 50
                      ? 'bg-amber-500'
                      : 'bg-blue-500'
                }`}
              />
              {/* Glow Effect */}
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${stat.riskLevel}%` }}
                transition={{ duration: 1, delay: 0.5 + i * 0.1, ease: 'easeOut' }}
                className={`absolute top-0 left-0 h-full w-full opacity-30 blur-[4px] ${
                  stat.riskLevel > 80
                    ? 'bg-red-500'
                    : stat.riskLevel > 50
                      ? 'bg-amber-500'
                      : 'bg-blue-500'
                }`}
              />
            </div>
            <p className="text-[10px] text-right mt-1 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">
              Risk Exposure: {stat.riskLevel}%
            </p>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 rounded-xl bg-white/5 border border-white/5">
        <p className="text-[10px] text-slate-400 leading-relaxed">
          <strong className="text-white">Insight:</strong> High concentration of assets in API
          endpoints increases injection attack vectors.
        </p>
      </div>
    </GlassCard>
  );
}
