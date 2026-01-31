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
import { GlobalVuln } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

export function GlobalVulnerabilityTable({ vulns }: { vulns: GlobalVuln[] }) {
  return (
    <div className="glass-panel p-6 rounded-[24px] relative overflow-hidden">
      <div className="flex items-center gap-2 mb-6">
        <div className="h-8 w-1 bg-red-500 rounded-full"></div>
        <h3 className="text-white font-bold text-lg">Global Vulnerability Stream</h3>
      </div>

      <Table>
        <TableHeader className="bg-white/5">
          <TableRow className="border-white/5 hover:bg-transparent">
            <TableHead className="text-[10px] uppercase text-slate-400 w-[120px]">CVE ID</TableHead>
            <TableHead className="text-[10px] uppercase text-slate-400">Vulnerability</TableHead>
            <TableHead className="text-[10px] uppercase text-slate-400">Severity</TableHead>
            <TableHead className="text-[10px] uppercase text-slate-400">Project</TableHead>
            <TableHead className="text-[10px] uppercase text-slate-400 text-right">
              Detected
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {vulns.map((v) => (
            <TableRow key={v.id} className="border-white/5 hover:bg-white/[0.02]">
              <TableCell>
                <span className="font-mono text-xs text-slate-300 bg-white/5 px-2 py-1 rounded border border-white/5 whitespace-nowrap">
                  {v.cveId}
                </span>
              </TableCell>
              <TableCell>
                <span
                  className="text-sm text-slate-200 font-medium truncate max-w-[200px] block"
                  title={v.title}
                >
                  {v.title}
                </span>
              </TableCell>
              <TableCell>
                <Badge
                  variant="outline"
                  className={`border-none ${
                    v.severity === 'critical'
                      ? 'bg-red-500/10 text-red-500'
                      : v.severity === 'high'
                        ? 'bg-orange-500/10 text-orange-500'
                        : 'bg-yellow-500/10 text-yellow-500'
                  }`}
                >
                  {v.severity.toUpperCase()}
                </Badge>
              </TableCell>
              <TableCell className="text-xs text-cyan-400 hover:text-cyan-300 cursor-pointer">
                {v.projectName}
              </TableCell>
              <TableCell className="text- right text-xs text-slate-500 font-mono text-right">
                {formatDistanceToNow(new Date(v.detectedAt), { addSuffix: true })}
              </TableCell>
            </TableRow>
          ))}
          {(!vulns || vulns.length === 0) && (
            <TableRow>
              <TableCell colSpan={5} className="h-24 text-center text-slate-500">
                System Secure. No open vulnerabilities detected.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
