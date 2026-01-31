'use client';

import { formatDistanceToNow } from 'date-fns';

interface RecentScansCardProps {
  scans: any[];
}

export function RecentScansCard({ scans }: RecentScansCardProps) {
  return (
    <div className="glass-panel p-6 rounded-[24px] h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold text-white">Recent Scans</h3>
      </div>
      <div className="space-y-4 flex-grow">
        {scans.map((scan) => {
          const isSuccess = scan.score >= 80;
          const isCritical = scan.score < 50;
          const isWarning = !isSuccess && !isCritical;

          const colorClass = isSuccess
            ? 'bg-emerald-500'
            : isCritical
              ? 'bg-red-500'
              : 'bg-orange-500';
          const textClass = isSuccess
            ? 'text-emerald-400'
            : isCritical
              ? 'text-red-400'
              : 'text-orange-400';
          const statusText = isSuccess ? 'PASSED' : isCritical ? 'CRITICAL FOUND' : 'WARNINGS';

          return (
            <div
              key={scan.id}
              className="p-3 rounded-xl bg-white/5 border border-white/5 relative overflow-hidden group hover:bg-white/10 transition-colors"
            >
              <div className={`absolute left-0 top-0 bottom-0 w-1 ${colorClass}`}></div>
              <div className="flex justify-between items-center mb-1">
                <span className={`text-xs font-mono ${textClass}`}>{statusText}</span>
                <span className="text-[10px] text-slate-500">
                  {formatDistanceToNow(new Date(scan.completed_at || scan.created_at), {
                    addSuffix: true,
                  })}
                </span>
              </div>
              <p className="text-sm font-medium text-white mb-1">{scan.type}</p>
              <div className="w-full bg-black/50 h-1 rounded-full overflow-hidden">
                <div className={`${colorClass} h-full`} style={{ width: `${scan.score}%` }}></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
