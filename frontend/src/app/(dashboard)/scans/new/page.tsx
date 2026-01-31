'use client';

import { ScanForm } from '@/components/scans/scan-form';
import { ScanPreview } from '@/components/scans/scan-preview';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

export default function NewScanPage() {
  return (
    <div className="max-w-[1600px] mx-auto animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2 text-sm font-mono">
            <Link href="/scans" className="text-slate-500 hover:text-white transition-colors">
              Scans
            </Link>
            <ChevronRight className="h-3 w-3 text-slate-600" />
            <span className="text-cyan-500">New Configuration</span>
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight">New Scan Configuration</h1>
          <p className="text-slate-400 text-lg font-light mt-2">
            Configure parameters and launch a security assessment.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-8 space-y-8">
          <ScanForm />
        </div>
        <div className="lg:col-span-4 space-y-6">
          <ScanPreview />
        </div>
      </div>
    </div>
  );
}
