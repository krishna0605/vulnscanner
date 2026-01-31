'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, Globe, Server, Hash, Layers, Settings, Shield, Clock } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';

import { createProject, updateProject } from '@/app/actions';
import { useRouter } from 'next/navigation';
import { logger } from '@/utils/logger';

interface ProjectFormProps {
  initialData?: any;
}

export function ProjectForm({ initialData }: ProjectFormProps) {
  const router = useRouter();
  const [targets, setTargets] = React.useState<{ id: number; value: string }[]>(
    initialData?.assets?.map((a: any) => ({ id: a.id, value: a.url })) || [{ id: 1, value: '' }]
  );
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const isEditMode = !!initialData;

  const addTarget = () => {
    setTargets([...targets, { id: Date.now(), value: '' }]);
  };

  const removeTarget = (id: number) => {
    if (targets.length > 1) {
      setTargets(targets.filter((t) => t.id !== id));
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    const formData = new FormData(e.currentTarget);

    // Append targets as JSON
    formData.append('targets', JSON.stringify(targets));

    try {
      if (isEditMode) {
        await updateProject(initialData.id, formData);
      } else {
        await createProject(formData);
      }
      router.push('/projects');
      router.refresh();
    } catch (error) {
      alert(`Failed to ${isEditMode ? 'update' : 'create'} project`);
      logger.error(`Failed to ${isEditMode ? 'update' : 'create'} project`, { error });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="glass-panel p-8 rounded-[24px] relative overflow-hidden"
    >
      {/* Step 01: Project Identity */}
      <div className="relative pb-10 border-l border-white/10 pl-8 ml-3">
        <span className="absolute -left-[19px] top-0 flex h-10 w-10 items-center justify-center rounded-full bg-[#313131] border border-white/20 ring-4 ring-[#313131] z-10 transition-all hover:scale-110 hover:border-cyan-500/50 cursor-pointer shadow-glow">
          <Layers className="h-4 w-4 text-cyan-400" />
        </span>
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          Project Identity
          <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-[10px] uppercase font-bold tracking-wider">
            Step 01
          </span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="col-span-2 space-y-2">
            <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
              Project Name
            </Label>
            <Input
              name="name"
              required
              defaultValue={initialData?.name}
              className="bg-white/5 border-white/10 text-white placeholder-slate-600 focus:border-cyan-500/50 focus:ring-cyan-500/20 h-12 rounded-xl text-lg font-medium"
              placeholder="e.g., Q3 Cloud Infrastructure Audit"
            />
          </div>
          <div className="col-span-2 space-y-2">
            <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
              Description
            </Label>
            <textarea
              name="description"
              defaultValue={initialData?.description}
              className="flex w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/20 focus-visible:border-cyan-500/50 disabled:cursor-not-allowed disabled:opacity-50 min-h-[100px] resize-none"
              placeholder="Describe the scope and purpose of this security project..."
            />
          </div>
          <div className="space-y-2">
            <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
              Department / Client
            </Label>
            <Input
              name="department"
              defaultValue={initialData?.department} // Note: This might not populate if not in DB schema, but safe to leave
              className="bg-white/5 border-white/10 text-white placeholder-slate-600 focus:border-cyan-500/50 focus:ring-cyan-500/20 h-11 rounded-xl"
              placeholder="e.g., Finance Dept"
            />
          </div>
          <div className="space-y-2">
            <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
              Project Lead
            </Label>
            <Input
              className="bg-white/5 border-white/10 text-white placeholder-slate-600 focus:border-cyan-500/50 focus:ring-cyan-500/20 h-11 rounded-xl"
              placeholder="e.g., John Doe"
            />
          </div>
        </div>
      </div>

      {/* Step 02: Target Scope */}
      <div className="relative pb-10 border-l border-white/10 pl-8 ml-3">
        <span className="absolute -left-[19px] top-0 flex h-10 w-10 items-center justify-center rounded-full bg-[#313131] border border-white/20 ring-4 ring-[#313131] z-10 transition-all hover:scale-110 hover:border-purple-500/50 cursor-pointer group">
          <Globe className="h-4 w-4 text-slate-400 group-hover:text-purple-400 transition-colors" />
        </span>
        <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
          Target Scope
          <span className="px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 text-[10px] uppercase font-bold tracking-wider">
            Step 02
          </span>
        </h3>
        <p className="text-slate-400 text-sm mb-6">
          Define the boundaries. Add all domains and IPs belonging to this project.
        </p>

        <div className="space-y-3">
          <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
            Target Domains / IPs
          </Label>
          <div className="space-y-3">
            <AnimatePresence>
              {targets.map((target: any, index: number) => (
                <motion.div
                  key={target.id}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="flex gap-2"
                >
                  <div className="relative flex-1">
                    <Globe className="absolute left-4 top-3.5 h-4 w-4 text-slate-600" />
                    <Input
                      value={target.value}
                      onChange={(e) => {
                        const newTargets = [...targets];
                        const t = newTargets.find((t: any) => t.id === target.id);
                        if (t) t.value = e.target.value;
                        setTargets(newTargets);
                      }}
                      className="bg-white/5 border-white/10 text-white placeholder-slate-600 focus:border-purple-500/50 focus:ring-purple-500/20 pl-12 h-11 rounded-xl font-mono text-sm"
                      placeholder="https://api.example.com"
                    />
                  </div>
                  {targets.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeTarget(target.id)}
                      className="h-11 w-11 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
          <Button
            type="button"
            onClick={addTarget}
            variant="outline"
            className="w-full mt-2 h-11 border-dashed border-white/20 text-slate-400 hover:text-white hover:bg-white/5 hover:border-white/40 rounded-xl flex items-center justify-center gap-2 group"
          >
            <Plus className="h-4 w-4 group-hover:scale-125 transition-transform" />
            Add Another Target
          </Button>
        </div>
      </div>

      {/* Step 03: Scan Defaults */}
      <div className="relative pl-8 ml-3 pb-8 border-l border-white/10">
        <span className="absolute -left-[19px] top-0 flex h-10 w-10 items-center justify-center rounded-full bg-[#313131] border border-white/20 ring-4 ring-[#313131] z-10 transition-all hover:scale-110 hover:border-emerald-500/50 cursor-pointer group">
          <Settings className="h-4 w-4 text-slate-400 group-hover:text-emerald-400 transition-colors" />
        </span>
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          Scan Defaults
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] uppercase font-bold tracking-wider">
            Step 03
          </span>
        </h3>

        <div className="bg-white/5 p-6 rounded-2xl border border-white/5 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
                Default Scan Profile
              </Label>
              <Select defaultValue="full">
                <SelectTrigger className="w-full h-11 bg-[#313131] border-white/10 text-white rounded-xl text-sm">
                  <SelectValue>Select Profile</SelectValue>
                </SelectTrigger>
                <SelectContent className="bg-[#313131] border-white/10 text-white">
                  <SelectItem value="quick">⚡ Quick Scan</SelectItem>
                  <SelectItem value="full">🛡️ Full Deep Scan</SelectItem>
                  <SelectItem value="pen">⚔️ Pen Test Mode</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
                Scan Frequency
              </Label>
              <Select defaultValue="weekly">
                <SelectTrigger className="w-full h-11 bg-[#313131] border-white/10 text-white rounded-xl text-sm">
                  <SelectValue>Select Frequency</SelectValue>
                </SelectTrigger>
                <SelectContent className="bg-[#313131] border-white/10 text-white">
                  <SelectItem value="daily">📅 Daily</SelectItem>
                  <SelectItem value="weekly">📅 Weekly</SelectItem>
                  <SelectItem value="monthly">📅 Monthly</SelectItem>
                  <SelectItem value="manual">✋ Manual Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="pt-4 border-t border-white/5">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <Shield className="h-4 w-4 text-emerald-400" />
                  Continuous Monitoring
                </h4>
                <p className="text-[10px] text-slate-400 mt-1">
                  Automatically scan for new subdomains and exposed assets.
                </p>
              </div>
              <Switch />
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-12 pt-8 border-t border-white/10 flex justify-end items-center gap-4">
        <Button
          onClick={() => router.back()}
          type="button"
          variant="ghost"
          className="text-slate-400 hover:text-white hover:bg-white/5 h-12 px-6 rounded-xl"
        >
          Cancel
        </Button>
        <Button
          disabled={isSubmitting}
          type="submit"
          className="bg-white text-black font-bold h-12 px-8 rounded-xl shadow-glow hover:shadow-glow-hover transition-all flex items-center gap-2"
        >
          <Plus className={`h-5 w-5 ${isSubmitting ? 'animate-spin' : ''}`} />
          {isSubmitting
            ? isEditMode
              ? 'Updating...'
              : 'Creating...'
            : isEditMode
              ? 'Update Project'
              : 'Create Project'}
        </Button>
      </div>
    </form>
  );
}
