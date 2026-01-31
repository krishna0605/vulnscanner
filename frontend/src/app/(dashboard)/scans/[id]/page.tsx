'use client';

import { useEffect, useState, useRef } from 'react';
import { createClient } from '@/utils/supabase/client';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Terminal, Play, Loader2, CheckCircle2, XCircle } from 'lucide-react';

interface ScanLog {
  id: number;
  message: string;
  level: 'info' | 'warn' | 'error' | 'success';
  timestamp: string;
}

interface Finding {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  description: string;
  evidence: string;
  remediation?: string;
}

interface ScanDetail {
  id: string;
  target_url: string;
  status: 'queued' | 'scanning' | 'completed' | 'failed';
  progress: number;
  current_action: string;
}

export default function ScanDetailsPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [scan, setScan] = useState<ScanDetail | null>(null);
  const [logs, setLogs] = useState<ScanLog[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const supabase = createClient();

  // Params unwrap removed - using direct id access

  // 2. Initial Data Fetch
  useEffect(() => {
    if (!id) return;

    const fetchData = async () => {
      // Fetch Scan
      const { data: scanData } = await supabase.from('scans').select('*').eq('id', id).single();
      if (scanData) setScan(scanData);

      // Fetch Logs
      const { data: logData } = await supabase
        .from('scan_logs')
        .select('*')
        .eq('scan_id', id)
        .order('id', { ascending: true });
      if (logData) setLogs(logData);

      // Fetch Findings
      const { data: findingData } = await supabase.from('findings').select('*').eq('scan_id', id);
      if (findingData) setFindings(findingData);
    };

    fetchData();

    // 3. Realtime Subscription
    const channel = supabase
      .channel(`scan:${id}`)
      .on(
        'postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'scans', filter: `id=eq.${id}` },
        (payload) => {
          setScan(payload.new as ScanDetail);
        }
      )
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'scan_logs', filter: `scan_id=eq.${id}` },
        (payload) => {
          setLogs((current) => [...current, payload.new as ScanLog]);
        }
      )
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'findings', filter: `scan_id=eq.${id}` },
        (payload) => {
          setFindings((current) => [...current, payload.new as Finding]);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [id, supabase]);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  if (!scan)
    return (
      <div className="p-8 flex items-center justify-center min-h-[500px]">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-500" />
      </div>
    );

  return (
    <div className="space-y-6 p-6 md:p-8 max-w-[1600px] mx-auto animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-bold tracking-tight text-white">Scan Details</h2>
            <Badge
              variant="outline"
              className={`
                ${
                  scan.status === 'completed'
                    ? 'border-emerald-500 text-emerald-500 bg-emerald-500/10'
                    : scan.status === 'failed'
                      ? 'border-red-500 text-red-500 bg-red-500/10'
                      : 'border-cyan-500 text-cyan-500 bg-cyan-500/10 animate-pulse'
                }
             `}
            >
              {scan.status.toUpperCase()}
            </Badge>
          </div>
          <div className="flex items-center gap-2 text-slate-400 font-mono text-sm">
            <span className="material-symbols-outlined text-[16px]">globe</span>
            {scan.target_url}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Progress Indicator */}
          {scan.status === 'scanning' && (
            <div className="flex items-center gap-3 mr-4">
              <div className="text-right">
                <p className="text-xs text-slate-400 font-mono">Current Action</p>
                <p className="text-sm text-cyan-400 font-bold animate-pulse">
                  {scan.current_action}
                </p>
              </div>
              <div className="relative h-12 w-12 flex items-center justify-center">
                <svg className="h-full w-full -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-slate-800"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="text-cyan-500 transition-all duration-500 ease-out"
                    strokeDasharray={`${scan.progress}, 100`}
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                </svg>
                <span className="absolute text-[10px] font-bold text-white">{scan.progress}%</span>
              </div>
            </div>
          )}

          <Button
            variant="destructive"
            disabled={scan.status === 'completed' || scan.status === 'failed'}
            className="gap-2"
            onClick={async () => {
              if (confirm('Are you sure you want to stop this scan?')) {
                await supabase
                  .from('scans')
                  .update({ status: 'failed', current_action: 'Stopped by user' })
                  .eq('id', id);
              }
            }}
          >
            <XCircle className="h-4 w-4" /> Stop Scan
          </Button>
          <Button
            variant="outline"
            disabled={scan.status !== 'completed'}
            className="gap-2 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
            onClick={() => {
              // Generate and download JSON report
              const reportData = {
                scan: {
                  id: scan.id,
                  target_url: scan.target_url,
                  status: scan.status,
                  progress: scan.progress,
                },
                findings: findings,
                logs: logs,
                generated_at: new Date().toISOString(),
              };
              const blob = new Blob([JSON.stringify(reportData, null, 2)], {
                type: 'application/json',
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `scan-report-${scan.id.slice(0, 8)}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            <CheckCircle2 className="h-4 w-4" /> Download Report
          </Button>
        </div>
      </div>

      <Tabs defaultValue="console" className="space-y-6">
        <TabsList className="bg-black/40 border border-white/10 p-1">
          <TabsTrigger
            value="console"
            className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400"
          >
            <Terminal className="mr-2 h-4 w-4" />
            Live Console
          </TabsTrigger>
          <TabsTrigger
            value="findings"
            className="data-[state=active]:bg-red-500/20 data-[state=active]:text-red-400"
          >
            <AlertTriangle className="mr-2 h-4 w-4" />
            Findings ({findings.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="console" className="space-y-4">
          <div className="rounded-xl border border-white/10 bg-black/90 p-4 font-mono text-sm h-[600px] overflow-auto shadow-[inset_0_0_20px_rgba(0,0,0,0.5)] custom-scrollbar">
            <div className="text-slate-500 mb-4 select-none"># Connected to scanner stream...</div>

            {logs.map((log) => (
              <div
                key={log.id}
                className="mb-2 flex gap-3 group hover:bg-white/5 p-0.5 rounded px-2 transition-colors"
              >
                <span className="text-slate-600 select-none text-xs pt-0.5 min-w-[140px]">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <div className="flex-1">
                  <span
                    className={`font-bold mr-2 uppercase text-[10px] tracking-wider
                          ${
                            log.level === 'info'
                              ? 'text-blue-400'
                              : log.level === 'warn'
                                ? 'text-amber-400'
                                : log.level === 'error'
                                  ? 'text-red-500'
                                  : 'text-emerald-400'
                          }
                      `}
                  >
                    [{log.level}]
                  </span>
                  <span className={`${log.level === 'error' ? 'text-red-400' : 'text-slate-300'}`}>
                    {log.message}
                  </span>
                </div>
              </div>
            ))}

            {scan.status === 'scanning' && (
              <div className="mt-4 flex items-center gap-2 text-cyan-500 animate-pulse px-2">
                <span className="w-2 h-4 bg-cyan-500 block"></span>
                <span>_Processing...</span>
              </div>
            )}

            <div ref={logsEndRef} />
          </div>
        </TabsContent>

        <TabsContent value="findings" className="space-y-4">
          <div className="grid gap-4">
            {findings.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-white/10 rounded-xl">
                <p className="text-slate-500">No vulnerabilities found yet.</p>
              </div>
            ) : (
              findings.map((f) => (
                <div
                  key={f.id}
                  className="group relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-all duration-300"
                >
                  {/* Severity Stripe */}
                  <div
                    className={`absolute left-0 top-0 bottom-0 w-1 ${
                      f.severity === 'critical'
                        ? 'bg-red-600'
                        : f.severity === 'high'
                          ? 'bg-orange-500'
                          : f.severity === 'medium'
                            ? 'bg-amber-400'
                            : 'bg-blue-400'
                    }`}
                  ></div>

                  <div className="p-6 pl-8">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-bold text-lg text-white mb-1">{f.title}</h4>
                        <p className="text-sm text-slate-400">{f.description}</p>
                      </div>
                      <Badge
                        variant="outline"
                        className={`uppercase tracking-widest text-[10px] ${
                          f.severity === 'critical'
                            ? 'border-red-500 text-red-500'
                            : f.severity === 'high'
                              ? 'border-orange-500 text-orange-500'
                              : f.severity === 'medium'
                                ? 'border-amber-500 text-amber-500'
                                : 'border-blue-500 text-blue-500'
                        }`}
                      >
                        {f.severity}
                      </Badge>
                    </div>

                    {f.evidence && (
                      <div className="mt-4 bg-black/50 rounded-lg p-3 border border-white/5 font-mono text-xs text-slate-300 overflow-x-auto">
                        {f.evidence}
                      </div>
                    )}

                    {f.remediation && (
                      <div className="mt-4 flex items-start gap-2 text-sm text-emerald-400/80">
                        <CheckCircle2 className="h-4 w-4 mt-0.5" />
                        <p>{f.remediation}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
