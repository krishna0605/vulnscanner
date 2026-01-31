'use client';

import { Target, Sliders, Timer, Zap, Database, Globe, Folder, PlusCircle } from 'lucide-react';

export function ScanPreview() {
  return (
    <div className="space-y-6">
      {/* Preview Card */}
      <div className="glass-panel p-6 rounded-[24px]">
        <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/5">
          <h3 className="text-lg font-bold text-white">Scan Preview</h3>
          <span className="inline-flex items-center px-2 py-1 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-400 uppercase tracking-wide border border-cyan-500/20">
            Draft
          </span>
        </div>

        <div className="space-y-5">
          <div className="flex items-start gap-3">
            <div className="mt-1 w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-slate-400 border border-white/10 shrink-0">
              <Target className="h-4 w-4" />
            </div>
            <div className="overflow-hidden">
              <p className="text-[10px] uppercase text-slate-500 tracking-wider font-mono">
                Target
              </p>
              <p className="text-sm text-slate-300 break-all truncate">https://app.example.com</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="mt-1 w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-slate-400 border border-white/10 shrink-0">
              <Sliders className="h-4 w-4" />
            </div>
            <div>
              <p className="text-[10px] uppercase text-slate-500 tracking-wider font-mono">
                Profile
              </p>
              <p className="text-sm text-white">Full Deep Scan</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="mt-1 w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-slate-400 border border-white/10 shrink-0">
              <Timer className="h-4 w-4" />
            </div>
            <div>
              <p className="text-[10px] uppercase text-slate-500 tracking-wider font-mono">
                Est. Duration
              </p>
              <p className="text-sm text-slate-300">~ 2 Hours 15 Mins</p>
            </div>
          </div>
        </div>

        <div className="mt-6 p-3 bg-cyan-900/20 border border-cyan-500/20 rounded-lg flex items-center gap-3">
          <Zap className="h-4 w-4 text-cyan-400 fill-current" />
          <p className="text-xs text-cyan-100">
            Credit usage: <span className="font-bold">25 Credits</span>
          </p>
        </div>
      </div>

      {/* Asset Selector */}
      <div className="glass-panel p-6 rounded-[24px]">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 font-mono">
          Quick Select Assets
        </h3>
        <div className="space-y-2">
          <div className="group flex items-center p-3 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 cursor-pointer transition-all">
            <div className="w-8 h-8 rounded bg-indigo-500/20 flex items-center justify-center text-indigo-300 mr-3 shrink-0">
              <Database className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium group-hover:text-cyan-400 transition-colors truncate">
                Production DB
              </p>
              <p className="text-[10px] text-slate-500 truncate">10.0.24.15</p>
            </div>
            <PlusCircle className="h-4 w-4 text-slate-600 opacity-0 group-hover:opacity-100 transition-all transform group-hover:rotate-90" />
          </div>

          <div className="group flex items-center p-3 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 cursor-pointer transition-all">
            <div className="w-8 h-8 rounded bg-emerald-500/20 flex items-center justify-center text-emerald-300 mr-3 shrink-0">
              <Globe className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium group-hover:text-cyan-400 transition-colors truncate">
                Public Gateway
              </p>
              <p className="text-[10px] text-slate-500 truncate">api.cyberguard.io</p>
            </div>
            <PlusCircle className="h-4 w-4 text-slate-600 opacity-0 group-hover:opacity-100 transition-all transform group-hover:rotate-90" />
          </div>

          <div className="group flex items-center p-3 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 cursor-pointer transition-all">
            <div className="w-8 h-8 rounded bg-orange-500/20 flex items-center justify-center text-orange-300 mr-3 shrink-0">
              <Folder className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium group-hover:text-cyan-400 transition-colors truncate">
                Staging Cluster
              </p>
              <p className="text-[10px] text-slate-500 truncate">k8s-stage-01</p>
            </div>
            <PlusCircle className="h-4 w-4 text-slate-600 opacity-0 group-hover:opacity-100 transition-all transform group-hover:rotate-90" />
          </div>
        </div>

        <button className="w-full mt-4 py-2 text-xs text-slate-500 hover:text-white border border-dashed border-slate-700 hover:border-slate-500 rounded-lg transition-all hover:bg-white/5">
          + Add New Asset Source
        </button>
      </div>
    </div>
  );
}
