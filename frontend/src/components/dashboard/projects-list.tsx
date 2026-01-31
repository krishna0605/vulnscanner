'use client';

import { motion } from 'framer-motion';
import { EmptyState } from '@/components/ui/empty-state';

interface Project {
  id: string;
  name: string;
  target_urls: string[];
  status: string;
  // We would need to join scans/vulns for exact details, using mock defaults for demo if missing
}

export function ProjectsList({ projects = [] }: { projects?: Project[] }) {
  return (
    <div className="glass-card rounded-[24px] overflow-hidden border border-white/5 bg-white/[0.02] backdrop-blur-xl">
      <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
        <h3 className="text-xl font-bold text-white">My Projects</h3>
        <a
          className="text-xs text-slate-400 hover:text-white font-mono flex items-center transition-colors cursor-pointer"
          href="/projects"
        >
          VIEW ALL <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
        </a>
      </div>
      <div className="p-2">
        <div className="hidden md:grid grid-cols-12 px-6 py-3 text-xs font-mono text-slate-500 uppercase tracking-wider">
          <div className="col-span-4">Project Name</div>
          <div className="col-span-3">Target</div>
          <div className="col-span-3">Status</div>
          <div className="col-span-2 text-right">Actions</div>
        </div>

        {projects.length === 0 && (
          <div className="p-4">
            <EmptyState
              icon="layers"
              title="No Projects"
              message="Create your first project to get started."
              className="min-h-[150px] border-none bg-transparent"
            />
          </div>
        )}

        {projects.map((project, index) => (
          <motion.div
            key={project.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            className="grid grid-cols-1 md:grid-cols-12 items-center px-6 py-4 hover:bg-white/5 rounded-xl transition-colors cursor-pointer group"
          >
            <div className="col-span-12 md:col-span-4 mb-2 md:mb-0">
              <div className="flex items-center">
                <div className="w-8 h-8 rounded bg-white/5 flex items-center justify-center mr-3 border border-white/10 text-white group-hover:bg-white/10 transition-colors">
                  <span className="material-symbols-outlined text-lg">layers</span>
                </div>
                <div>
                  <p className="text-white font-medium text-sm group-hover:text-cyan-400 transition-colors">
                    {project.name}
                  </p>
                </div>
              </div>
            </div>

            <div className="col-span-4 md:col-span-3 text-sm text-slate-400 font-mono truncate">
              {project.target_urls?.[0] || 'No target'}
            </div>

            <div className="col-span-4 md:col-span-3 my-2 md:my-0">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border
                ${project.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-500/10 text-slate-400'}
              `}
              >
                {project.status === 'active' && (
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-2 animate-pulse"></span>
                )}
                {project.status}
              </span>
            </div>

            <div className="col-span-4 md:col-span-2 flex justify-end space-x-1 items-center">
              <button className="text-slate-500 hover:text-white transition-colors">
                <span className="material-symbols-outlined">more_vert</span>
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
