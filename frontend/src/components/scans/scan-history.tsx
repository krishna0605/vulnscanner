'use client';

import { useEffect, useState } from 'react';
import {
  Filter,
  Download,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
} from 'lucide-react';
import Link from 'next/link';
import { EmptyState } from '@/components/ui/empty-state';
import { getScanHistory, HistoryScanItem } from '@/lib/api-client';

import { createClient } from '@/utils/supabase/client';

export function ScanHistory() {
  const [history, setHistory] = useState<HistoryScanItem[]>([]);
  const supabase = createClient();

  const fetchHistory = async () => {
    const data = await getScanHistory();
    setHistory(data);
  };

  useEffect(() => {
    fetchHistory();

    const channel = supabase
      .channel('history-realtime')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'scans',
          filter: 'status=in.(completed,failed)',
        },
        () => {
          fetchHistory();
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'scans',
          filter: 'status=in.(completed,failed)',
        },
        () => {
          fetchHistory();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <div className="glass-panel rounded-[24px] overflow-hidden">
      <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
        <h3 className="text-xl font-bold text-white">Recent Scans History</h3>
        <div className="flex space-x-2">
          <button className="flex items-center gap-2 text-[10px] font-mono text-slate-400 hover:text-white px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-lg transition-colors border border-white/5">
            <Filter className="h-3 w-3" /> FILTER
          </button>
          <button className="flex items-center gap-2 text-[10px] font-mono text-slate-400 hover:text-white px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-lg transition-colors border border-white/5">
            <Download className="h-3 w-3" /> EXPORT
          </button>
        </div>
      </div>

      <div className="p-2">
        <div className="grid grid-cols-12 px-6 py-3 text-[10px] font-mono text-slate-500 uppercase tracking-widest border-b border-white/5">
          <div className="col-span-4">Scan Name / Target</div>
          <div className="col-span-2">Completed</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-3 text-center">Severity Found</div>
          <div className="col-span-1 text-right">Report</div>
        </div>

        <div className="space-y-1 mt-2">
          {history.length === 0 && (
            <div className="py-12">
              <EmptyState
                icon="history"
                title="No Scan History"
                message="Your completed scans will be listed here."
                className="border-none bg-transparent"
              />
            </div>
          )}

          {history.map((scan) => (
            <Link key={scan.id} href={`/scans/${scan.id}`} className="block">
              <div className="grid grid-cols-12 items-center px-6 py-4 hover:bg-white/5 rounded-2xl transition-all cursor-pointer group border border-transparent hover:border-white/5">
                <div className="col-span-4">
                  <div className="flex items-center">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center mr-4 border ${
                        scan.statusType === 'success'
                          ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                          : scan.statusType === 'danger'
                            ? 'bg-red-500/10 border-red-500/20 text-red-400'
                            : 'bg-orange-500/10 border-orange-500/20 text-orange-400'
                      }`}
                    >
                      {scan.statusType === 'success' && <ShieldCheck className="h-5 w-5" />}
                      {scan.statusType === 'danger' && <AlertOctagon className="h-5 w-5" />}
                      {scan.statusType === 'warning' && <AlertTriangle className="h-5 w-5" />}
                    </div>
                    <div>
                      <p className="text-white font-bold text-sm tracking-tight group-hover:text-cyan-400 transition-colors">
                        {scan.name}
                      </p>
                      <p className="text-slate-500 text-[10px] uppercase tracking-wide mt-0.5">
                        {scan.target}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-span-2 text-xs text-slate-400 font-mono">{scan.completed}</div>
                <div className="col-span-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide border ${
                      scan.statusType === 'success'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : scan.statusType === 'danger'
                          ? 'bg-red-500/10 text-red-400 border-red-500/20'
                          : 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                    }`}
                  >
                    {scan.status}
                  </span>
                </div>
                <div className="col-span-3 flex justify-center space-x-4 text-xs font-mono">
                  <span className={scan.high > 0 ? 'text-red-400 font-bold' : 'text-slate-600'}>
                    {scan.high} High
                  </span>
                  <span className={scan.med > 0 ? 'text-orange-400' : 'text-slate-600'}>
                    {scan.med} Med
                  </span>
                  <span className="text-blue-400">{scan.low} Low</span>
                </div>
                <div className="col-span-1 flex justify-end">
                  <div className="text-slate-500 hover:text-white transition-colors flex items-center justify-center h-8 w-8 rounded-full hover:bg-white/10">
                    <ArrowRight className="h-4 w-4" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
