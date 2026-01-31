'use client';

import { motion } from 'framer-motion';
import { ChevronRight, Settings } from 'lucide-react';

const contributors = [
  {
    id: 1,
    name: 'Alex Knight',
    role: 'Security Engineer',
    avatar: 'AK',
    color: 'bg-indigo-500',
    status: 'online',
  },
  {
    id: 2,
    name: 'Maria Ross',
    role: 'DevOps Lead',
    avatar: 'MR',
    color: 'bg-purple-600',
    status: 'online',
  },
  {
    id: 3,
    name: 'Steve Jobs',
    role: 'Contributor',
    avatar: 'SJ',
    color: 'bg-blue-500',
    status: 'off',
  },
];

export function ContributorsList() {
  return (
    <div className="glass-panel rounded-[24px] p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-white font-bold text-lg">Active Contributors</h3>
        <button className="text-slate-400 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-white/5">
          <Settings className="h-4 w-4" />
        </button>
      </div>

      <div className="space-y-4">
        {contributors.map((person, idx) => (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 + 0.5 }}
            key={person.id}
            className="flex items-center justify-between group cursor-pointer p-2.5 rounded-2xl hover:bg-white/5 border border-transparent hover:border-white/5 transition-all"
          >
            <div className="flex items-center">
              <div className="relative">
                <div
                  className={`h-10 w-10 rounded-full ${person.color} border border-white/10 flex items-center justify-center text-sm font-bold text-white shadow-lg`}
                >
                  {person.avatar}
                </div>
                {person.status === 'online' && (
                  <div className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-emerald-500 border-2 border-[#313131]"></div>
                )}
              </div>
              <div className="ml-3">
                <p className="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors uppercase tracking-tight">
                  {person.name}
                </p>
                <p className="text-[10px] text-slate-500 font-mono mt-0.5">{person.role}</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-slate-600 group-hover:text-white transition-all transform group-hover:translate-x-1" />
          </motion.div>
        ))}
      </div>

      <button className="w-full mt-8 py-2.5 rounded-xl border border-white/10 text-[10px] font-bold text-slate-400 hover:text-white hover:bg-white/10 transition-all uppercase tracking-widest font-mono">
        Manage Team
      </button>
    </div>
  );
}
