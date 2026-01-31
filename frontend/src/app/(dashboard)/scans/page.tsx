'use client';

import { ScanStats } from '@/components/scans/scan-stats';
import { ActiveScans } from '@/components/scans/active-scans';
import { ScanHistory } from '@/components/scans/scan-history';
import { Button } from '@/components/ui/button';
import { Radar } from 'lucide-react';
import Link from 'next/link';

export default function ScansPage() {
  return (
    <div className="max-w-[1600px] mx-auto animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-6">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Scans</h1>
          <p className="text-slate-400 text-lg font-light">
            Monitor and launch security assessments
          </p>
        </div>
        <div className="flex space-x-4">
          <Link href="/scans/new">
            <Button className="h-12 px-8 rounded-2xl bg-white text-black font-mono text-[10px] font-bold hover:bg-slate-200 transition-all shadow-glow hover:shadow-glow-hover uppercase tracking-widest flex items-center">
              <Radar className="mr-2 h-4 w-4" />
              New Scan
            </Button>
          </Link>
        </div>
      </div>

      <ScanStats />
      <ActiveScans />
      <ScanHistory />
    </div>
  );
}
