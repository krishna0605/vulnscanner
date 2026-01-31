'use client';

import { useEffect, useState } from 'react';
import { Calendar, Timer, CheckCircle, TrendingUp } from 'lucide-react';
import { getScanStats } from '@/lib/api-client';

import { createClient } from '@/utils/supabase/client';

export function ScanStats() {
  const [stats, setStats] = useState({ monthCount: 0, avgDuration: '-', successRate: '-' });
  const supabase = createClient();

  const fetchStats = async () => {
    const data = await getScanStats();
    setStats(data);
  };

  useEffect(() => {
    fetchStats();

    const channel = supabase
      .channel('stats-realtime')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'scans' }, () => {
        fetchStats();
      })
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Scans This Month */}
      <div className="glass-panel p-6 rounded-[24px] hover:bg-white/5 transition-colors group relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl -mr-6 -mt-6 transition-all group-hover:bg-emerald-500/20"></div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 group-hover:text-white transition-colors">
            <Calendar className="h-6 w-6" />
          </div>
        </div>
        <h3 className="text-4xl font-bold text-white mb-1 tracking-tight">{stats.monthCount}</h3>
        <p className="text-slate-400 text-sm font-medium">Scans This Month</p>
      </div>

      {/* Average Duration */}
      <div className="glass-panel p-6 rounded-[24px] hover:bg-white/5 transition-colors group relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl -mr-6 -mt-6 transition-all group-hover:bg-blue-500/20"></div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 group-hover:text-white transition-colors">
            <Timer className="h-6 w-6" />
          </div>
        </div>
        <h3 className="text-4xl font-bold text-white mb-1 tracking-tight">{stats.avgDuration}</h3>
        <p className="text-slate-400 text-sm font-medium">Average Duration</p>
      </div>

      {/* Success Rate */}
      <div className="glass-panel p-6 rounded-[24px] hover:bg-white/5 transition-colors group relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl -mr-6 -mt-6 transition-all group-hover:bg-purple-500/20"></div>
        <div className="flex justify-between items-start mb-4">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 group-hover:text-white transition-colors">
            <CheckCircle className="h-6 w-6" />
          </div>
        </div>
        <h3 className="text-4xl font-bold text-white mb-1 tracking-tight">{stats.successRate}</h3>
        <p className="text-slate-400 text-sm font-medium">Successful Scans %</p>
      </div>
    </div>
  );
}
