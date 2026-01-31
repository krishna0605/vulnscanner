'use client';

import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { EmptyState } from '@/components/ui/empty-state';

interface Log {
  id: string;
  action_type: string;
  description: string;
  created_at: string;
}

export function RecentActivityFeed({ logs = [] }: { logs?: Log[] }) {
  // Helper to map action types to icons and colors
  const getMeta = (type: string) => {
    switch (type) {
      case 'scan_completed':
        return {
          icon: 'check_circle',
          color: 'bg-emerald-500/20 text-emerald-400',
          border: 'border-emerald-500/20',
        };
      case 'issue_found':
        return {
          icon: 'bug_report',
          color: 'bg-red-500/20 text-red-400',
          border: 'border-red-500/20',
          animate: true,
        };
      case 'project_created':
        return {
          icon: 'layers',
          color: 'bg-indigo-500/20 text-indigo-400',
          border: 'border-indigo-500/20',
        };
      default:
        return {
          icon: 'notifications',
          color: 'bg-blue-500/20 text-blue-400',
          border: 'border-blue-500/20',
        };
    }
  };

  return (
    <div className="glass-card p-6 rounded-[24px] h-full border border-white/5 bg-white/[0.02] backdrop-blur-xl">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-white">Recent Activity</h3>
        <button className="text-slate-400 hover:text-white transition-colors">
          <span className="material-symbols-outlined">filter_list</span>
        </button>
      </div>

      <div className="relative pl-4 h-[300px] overflow-y-auto custom-scrollbar pr-2">
        <div className="absolute left-[27px] top-2 bottom-4 w-px bg-gradient-to-b from-white/10 via-white/5 to-transparent"></div>

        {logs.length === 0 && (
          <div className="py-8">
            <EmptyState
              icon="notifications_off"
              title="No Activity"
              message="Recent system events will appear here."
              className="min-h-[150px] border-none bg-transparent"
            />
          </div>
        )}

        {logs.map((item, index) => {
          const meta = getMeta(item.action_type);
          return (
            <motion.div
              key={item.id || index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative flex gap-4 mb-8 last:mb-0 group"
            >
              <div
                className={`relative z-10 flex-shrink-0 w-8 h-8 rounded-full ${meta.color} border ${meta.border} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}
              >
                <span
                  className={`material-symbols-outlined text-sm ${meta.animate ? 'animate-pulse' : ''}`}
                >
                  {meta.icon}
                </span>
              </div>
              <div>
                <p className="text-sm text-slate-200 font-medium group-hover:text-white transition-colors capitalize">
                  {item.action_type.replace('_', ' ')}
                </p>
                <p className="text-xs text-slate-400 mt-1">{item.description}</p>
                <p className="text-[10px] text-slate-500 mt-2 font-mono">
                  {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
