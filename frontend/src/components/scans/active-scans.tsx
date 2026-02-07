'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Pause, Play, Square, Cloud, Database, Globe, Loader2 } from 'lucide-react';
import { getActiveScans, ActiveScanItem, pauseScan, resumeScan, cancelScan } from '@/lib/api-client';
import Link from 'next/link';
import { createClient } from '@/utils/supabase/client';

export function ActiveScans() {
  const [activeScans, setActiveScans] = useState<ActiveScanItem[]>([]);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  const fetchScans = async () => {
    // Don't show global loading on refresh, just background update
    if (activeScans.length === 0) setLoading(true);
    const data = await getActiveScans();
    setActiveScans(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchScans();

    // Realtime Subscription
    const channel = supabase
      .channel('scans-realtime')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'scans',
          filter: 'status=in.(pending,processing,scanning,paused,queued)',
        },
        (payload) => {
          // Optimistic update for progress/status
          setActiveScans((current) =>
            current.map((scan) => {
              if (scan.id === payload.new.id) {
                const newData = payload.new as any;
                return {
                  ...scan,
                  // Update fields with fallback logic matching getActiveScans
                  progress: newData.progress ?? scan.progress,
                  status:
                    newData.current_action ||
                    (newData.status ? newData.status.toUpperCase() : scan.status),
                  node: newData.node || scan.node,
                };
              }
              return scan;
            })
          );
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'scans',
        },
        () => {
          // New scan started, refresh full list to get relations
          fetchScans();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <div className="glass-panel rounded-[24px] overflow-hidden mb-8">
      <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
        <div className="flex items-center space-x-3">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse shadow-[0_0_10px_#3b82f6]"></div>
          <h3 className="text-xl font-bold text-white">Active Scans</h3>
          <span className="px-2.5 py-0.5 rounded-full bg-white/10 text-[10px] text-white font-mono border border-white/5">
            {activeScans.length} Running
          </span>
        </div>
        <button
          onClick={fetchScans}
          disabled={loading}
          className="text-slate-400 hover:text-white transition-colors p-2 hover:bg-white/5 rounded-full disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-400">
          <thead className="text-[10px] uppercase bg-white/[0.02] text-slate-300 font-mono tracking-wider">
            <tr>
              <th className="px-6 py-4 font-medium" scope="col">
                Target Domain
              </th>
              <th className="px-6 py-4 font-medium" scope="col">
                Engine Node
              </th>
              <th className="px-6 py-4 font-medium w-1/3" scope="col">
                Progress
              </th>
              <th className="px-6 py-4 font-medium" scope="col">
                Started
              </th>
              <th className="px-6 py-4 font-medium text-right" scope="col">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {activeScans.length === 0 && !loading && (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-500 font-mono text-xs">
                  No active scans running.{' '}
                  <Link href="/scans/new" className="text-cyan-400 hover:underline">
                    Start one?
                  </Link>
                </td>
              </tr>
            )}

            {activeScans.map((scan) => {
              // Dynamic Icon Mapping
              const Icon =
                scan.type === 'database' ? Database : scan.type === 'cloud' ? Cloud : Globe;

              return (
                <tr key={scan.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="px-6 py-5 font-medium text-white">
                    <div className="flex items-center gap-4">
                      <div
                        className={`p-2.5 rounded-xl border ${
                          scan.color === 'blue'
                            ? 'bg-blue-500/10 border-blue-500/20 text-blue-400'
                            : scan.color === 'emerald'
                              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                              : 'bg-orange-500/10 border-orange-500/20 text-orange-400'
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <Link
                          href={`/scans/${scan.id}`}
                          className="font-bold text-sm tracking-tight hover:underline hover:text-cyan-400 transition-colors"
                        >
                          {scan.target}
                        </Link>
                        <div className="text-[10px] text-slate-500 font-mono mt-0.5">{scan.ip}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <span className="px-2 py-1 rounded-md bg-white/5 border border-white/10 font-mono text-[10px] text-slate-300">
                      {scan.node}
                    </span>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex justify-between text-[10px] uppercase font-bold mb-2 tracking-wider">
                      <span
                        className={
                          scan.color === 'blue'
                            ? 'text-blue-400'
                            : scan.color === 'emerald'
                              ? 'text-emerald-400'
                              : 'text-orange-400'
                        }
                      >
                        {scan.status}
                      </span>
                      <span className="text-white">{scan.progress}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${scan.progress || 0}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                        className={`h-full rounded-full ${
                          scan.color === 'blue'
                            ? 'bg-blue-500 shadow-[0_0_10px_#3b82f6]'
                            : scan.color === 'emerald'
                              ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]'
                              : 'bg-orange-400 shadow-[0_0_10px_#fb923c]'
                        }`}
                      />
                    </div>
                  </td>
                  <td className="px-6 py-5 text-xs font-mono text-slate-400">{scan.started}</td>
                  <td className="px-6 py-5 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={async () => {
                          // Toggle pause/resume based on current status
                          const isPaused = scan.status === 'PAUSED' || scan.status === 'Paused by user';
                          if (isPaused) {
                            await resumeScan(scan.id);
                          } else {
                            await pauseScan(scan.id);
                          }
                          fetchScans(); // Refresh to show updated status
                        }}
                        className={`p-2 rounded-lg transition-colors ${
                          scan.status === 'PAUSED' || scan.status === 'Paused by user'
                            ? 'text-green-400 hover:text-green-300 hover:bg-green-400/10'
                            : 'text-slate-400 hover:text-yellow-400 hover:bg-yellow-400/10'
                        }`}
                        title={scan.status === 'PAUSED' || scan.status === 'Paused by user' ? 'Resume Scan' : 'Pause Scan'}
                      >
                        {scan.status === 'PAUSED' || scan.status === 'Paused by user' ? (
                          <Play className="h-4 w-4" />
                        ) : (
                          <Pause className="h-4 w-4" />
                        )}
                      </button>
                      <button
                        onClick={async () => {
                          if (confirm('Are you sure you want to stop this scan?')) {
                            await cancelScan(scan.id);
                            fetchScans(); // Refresh to remove from active list
                          }
                        }}
                        className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
                        title="Stop Scan"
                      >
                        <Square className="h-4 w-4 fill-current" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
