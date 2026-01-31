'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';

interface DiscoveredVulnsTableProps {
  vulns: any[];
}

export function DiscoveredVulnsTable({ vulns }: DiscoveredVulnsTableProps) {
  return (
    <div className="glass-panel rounded-[24px] border border-white/10 overflow-hidden relative">
      <div className="p-6 border-b border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h3 className="text-xl font-bold text-white">Discovered Vulnerabilities</h3>

        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search by CVE or Name..."
              className="pl-9 pr-4 py-2 bg-black/20 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-white/30 w-full sm:w-64 placeholder-slate-500 transition-all focus:bg-white/5"
            />
          </div>
          <select className="bg-black/20 border border-white/10 text-slate-300 text-sm rounded-lg px-4 py-2 outline-none focus:border-white/30 cursor-pointer hover:bg-white/5 transition-colors">
            <option>All Severities</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <Table>
          <TableHeader className="bg-white/5 border-b border-white/10">
            <TableRow className="hover:bg-transparent border-white/5">
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-400 font-mono pl-6 py-4 font-medium">
                CVE / ID
              </TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-400 font-mono py-4 font-medium">
                Severity
              </TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-400 font-mono py-4 font-medium">
                Vulnerability Name
              </TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-400 font-mono py-4 font-medium">
                Location
              </TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-400 font-mono py-4 font-medium">
                Status
              </TableHead>
              <TableHead className="text-right text-[10px] uppercase tracking-wider text-slate-400 font-mono pr-6 py-4 font-medium">
                Detected
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {vulns.map((vuln) => (
              <TableRow
                key={vuln.id}
                className="border-b border-white/5 hover:bg-white/5 transition-colors group"
              >
                <TableCell className="font-mono text-xs text-slate-300 pl-6 py-4">
                  {vuln.cve_id || `VULN-${vuln.id.slice(0, 4).toUpperCase()}`}
                </TableCell>
                <TableCell className="py-4">
                  <span
                    className={`
                                        inline-flex items-center px-2.5 py-0.5 rounded border text-xs font-bold shadow-lg backdrop-blur-sm
                                        ${
                                          vuln.severity === 'critical'
                                            ? 'bg-red-500/10 border-red-500/30 text-red-200 shadow-glow-red'
                                            : vuln.severity === 'high'
                                              ? 'bg-orange-500/10 border-orange-500/30 text-orange-200 shadow-glow-orange'
                                              : vuln.severity === 'medium'
                                                ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-200'
                                                : 'bg-blue-500/10 border-blue-500/30 text-blue-200'
                                        }
                                    `}
                  >
                    {vuln.severity.toUpperCase()}
                  </span>
                </TableCell>
                <TableCell className="font-medium text-white text-sm group-hover:text-blue-300 transition-colors py-4">
                  {vuln.title}
                </TableCell>
                <TableCell className="font-mono text-xs text-slate-400 py-4">
                  {vuln.location || '/'}
                </TableCell>
                <TableCell className="py-4">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-1.5 h-1.5 rounded-full ${
                        vuln.status === 'open'
                          ? 'bg-red-500 animate-pulse'
                          : vuln.status === 'fixed'
                            ? 'bg-emerald-500'
                            : 'bg-slate-500'
                      }`}
                    ></div>
                    <span className="text-xs text-slate-300 capitalize">{vuln.status}</span>
                  </div>
                </TableCell>
                <TableCell className="text-right text-xs font-mono text-slate-400 pr-6 py-4">
                  {new Date(vuln.created_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </TableCell>
              </TableRow>
            ))}
            {(!vulns || vulns.length === 0) && (
              <TableRow>
                <TableCell colSpan={6} className="h-32 text-center text-slate-500">
                  No vulnerabilities found. Good job!
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination Footer */}
      <div className="p-4 border-t border-white/10 flex justify-between items-center bg-white/5">
        <span className="text-xs text-slate-400">
          Showing 1-{vulns.length || 0} of {vulns.length || 0} vulnerabilities
        </span>
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
            disabled
          >
            <span className="material-symbols-outlined text-sm">chevron_left</span>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <span className="material-symbols-outlined text-sm">chevron_right</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
