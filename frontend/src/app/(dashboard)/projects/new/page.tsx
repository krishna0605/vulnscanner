import { ProjectForm } from '@/components/projects/project-form';
import { ProjectPreview } from '@/components/projects/project-preview';
import { Layers } from 'lucide-react';

export default function NewProjectPage() {
  return (
    <div className="space-y-8 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-xl border border-white/5">
              <Layers className="h-6 w-6 text-cyan-400" />
            </div>
            Create New Project
          </h1>
          <p className="text-slate-400 text-lg font-light mt-2 ml-14">
            Initialize a new security scope and define your target assets.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Main Form Area */}
        <div className="xl:col-span-2">
          <ProjectForm />
        </div>

        {/* Sidebar Preview */}
        <div className="xl:col-span-1">
          <div className="sticky top-24">
            <ProjectPreview />
          </div>
        </div>
      </div>
    </div>
  );
}
