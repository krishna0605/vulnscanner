'use client';

import { motion } from 'framer-motion';
import { Layers, Globe, Shield, Zap, AlertCircle } from 'lucide-react';

export function ProjectPreview() {
  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-white/10">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">
          Project Preview
        </h3>

        {/* Card Preview */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-br from-[#2a2a2a] to-[#1a1a1a] p-5 rounded-xl border border-white/5 shadow-2xl relative overflow-hidden group"
        >
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
            <Layers className="h-24 w-24 text-white" />
          </div>

          <div className="flex items-start justify-between mb-4">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg">
              <Layers className="h-5 w-5 text-white" />
            </div>
            <div className="px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider">
              Active
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-lg font-bold text-white mb-1">New Project Name</h4>
            <p className="text-xs text-slate-400 line-clamp-2">
              Project description will appear here...
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-black/20 p-2 rounded-lg">
              <div className="text-[10px] text-slate-500 uppercase mb-1">Targets</div>
              <div className="text-sm font-mono text-white flex items-center gap-1">
                <Globe className="h-3 w-3 text-cyan-400" />
                <span>1 Asset</span>
              </div>
            </div>
            <div className="bg-black/20 p-2 rounded-lg">
              <div className="text-[10px] text-slate-500 uppercase mb-1">Frequency</div>
              <div className="text-sm font-mono text-white flex items-center gap-1">
                <Zap className="h-3 w-3 text-yellow-400" />
                <span>Weekly</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Quotas / Info */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-500/10 rounded-lg">
            <Shield className="h-5 w-5 text-blue-400" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Pro Plan Active</h4>
            <p className="text-[10px] text-slate-400">You can create unlimited projects.</p>
          </div>
        </div>
        <div className="w-full bg-white/5 rounded-full h-1.5 mb-2 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-cyan-400 h-full w-[35%]"></div>
        </div>
        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
          <span>3/10 Active Projects</span>
          <span>35% Usage</span>
        </div>
      </div>

      {/* Help Tip */}
      <div className="p-4 rounded-xl border border-yellow-500/10 bg-yellow-500/5 flex gap-3">
        <AlertCircle className="h-5 w-5 text-yellow-500 shrink-0" />
        <div>
          <h4 className="text-xs font-bold text-yellow-200 mb-1">Best Practice</h4>
          <p className="text-[10px] text-yellow-200/70 leading-relaxed">
            Group related assets (e.g., &quot;Marketing Sites&quot; or &quot;Internal Tools&quot;)
            into a single project for unified reporting and policy management.
          </p>
        </div>
      </div>
    </div>
  );
}
