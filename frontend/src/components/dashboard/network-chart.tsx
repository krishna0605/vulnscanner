'use client';

import { motion } from 'framer-motion';

interface NetworkData {
  created_at: string;
  traffic_in: number;
  traffic_out: number;
}

export function NetworkTrafficChart({ data = [] }: { data?: NetworkData[] }) {
  // Use the latest data point for the stats, or fallback
  const latest = data.length > 0 ? data[data.length - 1] : { traffic_in: 0, traffic_out: 0 };
  const totalTraffic = (latest.traffic_in + latest.traffic_out).toFixed(2);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2, duration: 0.5 }}
      className="lg:col-span-2 glass-card p-6 h-[400px] flex flex-col group border border-white/5 bg-white/[0.02] backdrop-blur-xl rounded-[24px]"
    >
      <div className="flex justify-between items-center mb-6 z-10">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-slate-400">insights</span>
          <h3 className="font-bold text-white">Active Network Traffic</h3>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-[10px] font-mono text-slate-400">LIVE FEED</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500 bg-white/5 px-2 py-0.5 rounded border border-white/10">
            {totalTraffic} Mbps
          </span>
        </div>
      </div>

      <div className="flex-1 relative mt-4 z-10">
        {/* Visual Wave Representation (Stylized) */}
        <svg
          className="w-full h-full overflow-visible"
          preserveAspectRatio="none"
          viewBox="0 0 400 150"
        >
          <defs>
            <linearGradient id="chartGradient" x1="0%" x2="0%" y1="0%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.2"></stop>
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0"></stop>
            </linearGradient>
          </defs>
          <line
            stroke="rgba(255,255,255,0.03)"
            strokeWidth="1"
            x1="0"
            x2="400"
            y1="30"
            y2="30"
          ></line>
          <line
            stroke="rgba(255,255,255,0.03)"
            strokeWidth="1"
            x1="0"
            x2="400"
            y1="75"
            y2="75"
          ></line>
          <line
            stroke="rgba(255,255,255,0.03)"
            strokeWidth="1"
            x1="0"
            x2="400"
            y1="120"
            y2="120"
          ></line>

          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: 'easeInOut' }}
            d="M0,150 L0,100 L40,110 L80,70 L120,90 L160,40 L200,60 L240,30 L280,80 L320,50 L360,70 L400,20 L400,150 Z"
            fill="url(#chartGradient)"
          ></motion.path>

          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: 'easeInOut' }}
            className="filter drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]"
            d="M0,100 L40,110 L80,70 L120,90 L160,40 L200,60 L240,30 L280,80 L320,50 L360,70 L400,20"
            fill="none"
            stroke="#22d3ee"
            strokeWidth="2.5"
          ></motion.path>

          <motion.circle
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2 }}
            className="filter drop-shadow-[0_0_10px_#22d3ee]"
            cx="400"
            cy="20"
            fill="#22d3ee"
            r="4"
          ></motion.circle>
        </svg>

        <div className="absolute left-0 bottom-[-20px] w-full flex justify-between text-[9px] font-mono text-slate-500">
          <span>T-60s</span>
          <span>T-45s</span>
          <span>T-30s</span>
          <span>T-15s</span>
          <span>NOW</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-12 border-t border-white/5 pt-6 z-10">
        <div className="space-y-1">
          <p className="text-[10px] font-mono text-slate-500 uppercase">Inbound</p>
          <p className="text-lg font-bold text-white">
            {latest.traffic_in.toFixed(1)}{' '}
            <span className="text-xs font-normal text-slate-400">Mbps</span>
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] font-mono text-slate-500 uppercase">Outbound</p>
          <p className="text-lg font-bold text-white">
            {latest.traffic_out.toFixed(1)}{' '}
            <span className="text-xs font-normal text-slate-400">Mbps</span>
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] font-mono text-slate-500 uppercase">Latency</p>
          <p className="text-lg font-bold text-emerald-400">
            14 <span className="text-xs font-normal text-slate-400">ms</span>
          </p>
        </div>
      </div>
    </motion.div>
  );
}
