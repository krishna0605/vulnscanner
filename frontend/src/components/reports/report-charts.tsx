'use client';

import { motion } from 'framer-motion';

interface SeverityDistribution {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

interface VulnerabilityType {
  name: string;
  count: number;
}

interface ReportVisualizationsProps {
  findings: any[];
  severityDistribution?: SeverityDistribution;
  vulnerabilityTypes?: VulnerabilityType[];
}

export function ReportVisualizations({
  findings = [],
  severityDistribution,
  vulnerabilityTypes,
}: ReportVisualizationsProps) {
  const total = findings.length || 1; // Avoid divide by zero

  // Use pre-calculated severity distribution if available, otherwise calculate from findings
  const stats =
    severityDistribution ||
    findings.reduce(
      (acc, curr) => {
        const sev = (curr.severity || 'info').toLowerCase();
        acc[sev as keyof typeof acc] = (acc[sev as keyof typeof acc] || 0) + 1;
        return acc;
      },
      { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
    );

  // Calculate type distribution from findings if not provided
  const typesFromFindings = findings.reduce(
    (acc, curr) => {
      const type = curr.category || curr.type || curr.title || 'Unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  // Cumulative for chart layers (Largest at bottom/back)
  // Layer 1 (Bottom): Total. Color: Teal (Low).
  // Layer 2: Crit + High + Med. Color: Yellow (Med).
  // Layer 3: Crit + High. Color: Orange (High).
  // Layer 4 (Top): Crit. Color: Red (Crit).

  const countCrit = stats.critical;
  const countHigh = stats.high;
  const countMed = stats.medium;
  const countLow = stats.low + stats.info; // Treat info as low for chart

  const pctCrit = (countCrit / total) * 100;
  const pctHigh = ((countCrit + countHigh) / total) * 100;
  const pctMed = ((countCrit + countHigh + countMed) / total) * 100;
  const pctLow = 100; // Full background ring

  // Use pre-calculated vulnerability types if available, otherwise calculate from findings
  const topTypes = vulnerabilityTypes
    ? vulnerabilityTypes.slice(0, 5).map((t) => ({
        name: t.name,
        count: t.count,
        pct: (t.count / total) * 100,
      }))
    : (Object.entries(typesFromFindings) as [string, number][])
        .map(([name, count]) => ({ name, count, pct: (count / total) * 100 }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

  const getTypeColor = (name: string) => {
    if (name.toLowerCase().includes('sql')) return 'bg-orange-500';
    if (name.toLowerCase().includes('xss')) return 'bg-yellow-500';
    if (name.toLowerCase().includes('csrf')) return 'bg-teal-500';
    if (name.toLowerCase().includes('deserialization')) return 'bg-rose-500';
    return 'bg-slate-500';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Severity Chart */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-panel p-8 rounded-[24px] flex flex-col"
      >
        <h3 className="text-lg font-bold text-white mb-8">Vulnerabilities by Severity</h3>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-10 flex-grow">
          <div className="relative w-48 h-48 group">
            <svg
              className="w-full h-full transform -rotate-90 hover:scale-105 transition-transform duration-500"
              viewBox="0 0 36 36"
            >
              {/* Background Ring */}
              <circle
                cx="18"
                cy="18"
                r="16"
                fill="none"
                stroke="#334155"
                strokeWidth="3"
                opacity="0.2"
              />

              {/* Low - Teal (Bottom Layer) */}
              <motion.circle
                initial={{ strokeDasharray: '0 100' }}
                animate={{ strokeDasharray: `${pctLow} 100` }}
                transition={{ duration: 1, ease: 'circOut' }}
                cx="18"
                cy="18"
                r="15.9155"
                fill="none"
                stroke="#14b8a6"
                strokeWidth="3"
              />

              {/* Medium - Yellow */}
              <motion.circle
                initial={{ strokeDasharray: '0 100' }}
                animate={{ strokeDasharray: `${pctMed} 100` }}
                transition={{ duration: 1.2, ease: 'circOut' }}
                cx="18"
                cy="18"
                r="15.9155"
                fill="none"
                stroke="#eab308"
                strokeWidth="3"
                strokeDashoffset="0"
              />

              {/* High - Orange */}
              <motion.circle
                initial={{ strokeDasharray: '0 100' }}
                animate={{ strokeDasharray: `${pctHigh} 100` }}
                transition={{ duration: 1.4, ease: 'circOut' }}
                cx="18"
                cy="18"
                r="15.9155"
                fill="none"
                stroke="#f97316"
                strokeWidth="3"
                strokeDashoffset="0"
              />

              {/* Critical - Rose (Top Layer) */}
              <motion.circle
                initial={{ strokeDasharray: '0 100' }}
                animate={{ strokeDasharray: `${pctCrit} 100` }}
                transition={{ duration: 1.6, ease: 'circOut' }}
                cx="18"
                cy="18"
                r="15.9155"
                fill="none"
                stroke="#f43f5e"
                strokeWidth="3"
                strokeDashoffset="0"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold text-white">{findings.length}</span>
              <span className="text-xs text-slate-400 uppercase tracking-widest">Total</span>
            </div>

            {/* Glow effect */}
            <div className="absolute inset-0 bg-cyan-500/5 rounded-full blur-3xl -z-10 group-hover:bg-cyan-500/10 transition-colors"></div>
          </div>

          <div className="grid grid-cols-2 gap-x-8 gap-y-4">
            {[
              { label: 'Critical', count: stats.critical, color: 'bg-rose-500' },
              { label: 'High', count: stats.high, color: 'bg-orange-500' },
              { label: 'Medium', count: stats.medium, color: 'bg-yellow-500' },
              { label: 'Low', count: stats.low + stats.info, color: 'bg-teal-500' },
            ].map((legend) => (
              <div key={legend.label} className="flex items-center group cursor-default">
                <span
                  className={`w-3 h-3 rounded-full ${legend.color} mr-3 group-hover:scale-125 transition-transform duration-300`}
                ></span>
                <span className="text-sm text-slate-300 flex justify-between w-full min-w-[80px]">
                  <span>{legend.label}</span>
                  <span className="font-mono text-slate-500">{legend.count}</span>
                </span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Top 5 Types */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-panel p-8 rounded-[24px]"
      >
        <h3 className="text-lg font-bold text-white mb-6">Top Vulnerability Types</h3>
        {topTypes.length === 0 ? (
          <div className="text-slate-500 italic">No vulnerabilities found.</div>
        ) : (
          <div className="space-y-6">
            {topTypes.map((type, idx) => {
              const color = getTypeColor(type.name);
              return (
                <div key={type.name} className="group">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300 group-hover:text-white transition-colors">
                      {type.name}
                    </span>
                    <span className="text-slate-500 text-xs">
                      {type.count} ({Math.round(type.pct)}%)
                    </span>
                  </div>
                  <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${type.pct}%` }}
                      transition={{ duration: 1, delay: 0.8 + idx * 0.1, ease: 'easeOut' }}
                      className={`h-full rounded-full ${color}`}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </motion.div>
    </div>
  );
}
