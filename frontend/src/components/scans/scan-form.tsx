'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/utils/supabase/client';
import { logger } from '@/utils/logger';

import { motion } from 'framer-motion';
import {
  Link2,
  Info,
  Calendar,
  Clock,
  Rocket,
  LockKeyhole,
  Database,
  Code2,
  Server,
  ShieldAlert,
} from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Gauge, Lock, Shield, Settings2, Fingerprint, Bug, Zap, Save } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

export function ScanForm() {
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    projectId: '',
    url: '',
    scanType: 'quick',
    maxDepth: 0,
    checkHeaders: true,
    checkMixedContent: true,
    checkComments: true,
    userAgent: 'chrome',
    isScheduled: false,
    scheduleCron: '0 0 * * *',
    // Advanced Configuration
    authEnabled: false,
    authUsername: '',
    authPassword: '',
    authLoginUrl: '',

    // Attack Vectors
    vectorSQLi: true,
    vectorXSS: true,
    vectorSSRF: false,
    vectorMisconfig: true,

    // Performance
    rateLimit: 10, // req/sec
    concurrency: 5,
  });
  const router = useRouter();
  const supabase = createClient();

  const [profiles, setProfiles] = useState<any[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<string>('');

  useEffect(() => {
    // Fetch Projects & Profiles
    async function initData() {
      const { data: projData } = await supabase.from('projects').select('id, name');
      if (projData) setProjects(projData);

      try {
        const {
          data: { session },
        } = await supabase.auth.getSession();
        const res = await fetch('/api/profiles', {
          headers: {
            Authorization: `Bearer ${session?.access_token}`,
          },
        });
        if (res.ok) {
          const profData = await res.json();
          // Backend returns { success: true, data: [...] }
          if (profData.success && Array.isArray(profData.data)) {
            setProfiles(profData.data);
          } else {
            setProfiles([]);
          }
        }
      } catch (e) {
        logger.error('Failed to fetch profiles', { error: e });
      }
    }
    initData();
  }, [supabase]); // added supabase dependency

  const handleProfileChange = (profileId: string) => {
    setSelectedProfileId(profileId);
    const profile = profiles.find((p) => p.id === profileId);
    if (profile && profile.config) {
      setFormData((prev) => ({
        ...prev,
        scanType: profile.config.scanType || 'standard',
        maxDepth: profile.config.maxDepth ?? 2,
        checkHeaders: profile.config.checkHeaders ?? true,
        checkMixedContent: profile.config.checkMixedContent ?? true,
        checkComments: profile.config.checkComments ?? true,
        authEnabled: profile.config.authEnabled ?? false,
        authLoginUrl: profile.config.authLoginUrl || '',
        authUsername: profile.config.authUsername || '',
        authPassword: profile.config.authPassword || '',
        vectorSQLi: profile.config.vectorSQLi ?? true,
        vectorXSS: profile.config.vectorXSS ?? true,
        vectorSSRF: profile.config.vectorSSRF ?? false,
        vectorMisconfig: profile.config.vectorMisconfig ?? true,
        rateLimit: profile.config.rateLimit ?? 10,
        concurrency: profile.config.concurrency ?? 5,
      }));
    }
  };

  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [newProfileDesc, setNewProfileDesc] = useState('');

  const handleSaveProfile = async () => {
    if (!newProfileName) return;

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      const res = await fetch('/api/profiles', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({
          name: newProfileName,
          description: newProfileDesc,
          config: {
            scanType: formData.scanType,
            maxDepth: formData.maxDepth,
            checkHeaders: formData.checkHeaders,
            checkMixedContent: formData.checkMixedContent,
            checkComments: formData.checkComments,
            authEnabled: formData.authEnabled,
            authLoginUrl: formData.authLoginUrl,
            authUsername: formData.authUsername,
            authPassword: formData.authPassword,
            vectorSQLi: formData.vectorSQLi,
            vectorXSS: formData.vectorXSS,
            vectorSSRF: formData.vectorSSRF,
            vectorMisconfig: formData.vectorMisconfig,
            rateLimit: formData.rateLimit,
            concurrency: formData.concurrency,
          },
        }),
      });

      if (res.ok) {
        const responseData = await res.json();
        // Backend returns { success: true, data: {...} }
        if (responseData.success && responseData.data) {
          const newProfile = responseData.data;
          setProfiles([...profiles, newProfile]);
          setSelectedProfileId(newProfile.id);
          setSaveDialogOpen(false);
          setNewProfileName('');
          setNewProfileDesc('');
          alert('Profile saved successfully!');
        } else {
          alert('Failed to save profile: Invalid response');
        }
      } else {
        alert('Failed to save profile');
      }
    } catch (e) {
      logger.error('Failed to start scan', { error: e });
      alert('Error saving profile');
    }
  };

  const handleStartScan = async () => {
    if (!formData.projectId || !formData.url) {
      alert('Please select a project and enter a target URL.');
      return;
    }

    setLoading(true);
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      const res = await fetch('/api/scans', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({
          projectId: formData.projectId,
          targetUrl: formData.url,
          config: {
            scanType: formData.scanType,
            maxDepth: formData.maxDepth,
            maxPages: formData.scanType === 'deep' ? 200 : 50,
            checkHeaders: formData.checkHeaders,
            checkMixedContent: formData.checkMixedContent,
            checkComments: formData.checkComments,
            isScheduled: formData.isScheduled,
            scheduleCron: formData.isScheduled ? formData.scheduleCron : null,
            authEnabled: formData.authEnabled,
            authLoginUrl: formData.authLoginUrl,
            authUsername: formData.authUsername,
            authPassword: formData.authPassword,
            vectorSQLi: formData.vectorSQLi,
            vectorXSS: formData.vectorXSS,
            vectorSSRF: formData.vectorSSRF,
            vectorMisconfig: formData.vectorMisconfig,
            rateLimit: formData.rateLimit,
            concurrency: formData.concurrency,
          },
        }),
      });
      const data = await res.json();
      // Handle wrapped response
      const scanId = data.success ? data.data?.id : data.id; 
      
      if (scanId) {
        router.push(`/scans/${scanId}`);
      } else {
        alert(data.error || 'Failed to start scan');
      }
    } catch (e) {
      logger.error('Error starting scan', { error: e });
      alert('Error starting scan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-8 rounded-[24px] relative overflow-hidden">
      {/* Step 01: Target Information */}
      <div className="relative pb-10 border-l border-white/10 pl-8 ml-3">
        <span className="absolute -left-[19px] top-0 flex h-10 w-10 items-center justify-center rounded-full bg-[#313131] border border-white/20 ring-4 ring-[#313131] z-10">
          <span className="text-cyan-400 text-sm font-bold font-mono">01</span>
        </span>
        <h3 className="text-xl font-bold text-white mb-6">Target Information</h3>
        <div className="grid grid-cols-1 gap-6">
          <div className="space-y-2">
            <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
              Select Project
            </Label>
            <Select onValueChange={(v: string) => setFormData({ ...formData, projectId: v })}>
              <SelectTrigger className="w-full h-12 bg-white/5 border-white/10 text-white rounded-xl">
                <SelectValue>Select a project...</SelectValue>
              </SelectTrigger>
              <SelectContent className="bg-[#313131] border-white/10 text-white">
                {projects.map((p) => (
                  <SelectItem key={p.id} value={p.id}>
                    {p.name}
                  </SelectItem>
                ))}
                {projects.length === 0 && <SelectItem value="none">No projects found</SelectItem>}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
              Target URL
            </Label>
            <div className="relative">
              <Link2 className="absolute left-4 top-3.5 h-5 w-5 text-slate-500" />
              <Input
                className="bg-white/5 border-white/10 text-white placeholder-slate-600 focus:border-cyan-500/50 focus:ring-cyan-500/20 pl-12 h-12 rounded-xl font-mono text-sm"
                placeholder="https://app.example.com"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Step 02: Scan Profile */}
      <div className="relative pb-10 border-l border-white/10 pl-8 ml-3">
        <span className="absolute -left-[19px] top-0 flex h-10 w-10 items-center justify-center rounded-full bg-[#313131] border border-white/20 ring-4 ring-[#313131] z-10">
          <span className="text-slate-400 text-sm font-bold font-mono group-hover:text-cyan-400 transition-colors">
            02
          </span>
        </span>

        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-white">Scan Profile</h3>

          <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="bg-white/5 border-white/10 hover:bg-white/10 text-cyan-400"
              >
                <Save className="mr-2 h-4 w-4" />
                Save Current Config
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1e1e1e] border-white/10 text-white">
              <DialogHeader>
                <DialogTitle>Save Scan Profile</DialogTitle>
                <DialogDescription className="text-slate-400">
                  Save your current configuration settings as a reusable profile.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right text-slate-400">
                    Name
                  </Label>
                  <Input
                    id="name"
                    value={newProfileName}
                    onChange={(e) => setNewProfileName(e.target.value)}
                    className="col-span-3 bg-white/5 border-white/10 text-white"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="desc" className="text-right text-slate-400">
                    Description
                  </Label>
                  <Input
                    id="desc"
                    value={newProfileDesc}
                    onChange={(e) => setNewProfileDesc(e.target.value)}
                    className="col-span-3 bg-white/5 border-white/10 text-white"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="submit"
                  onClick={handleSaveProfile}
                  className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold"
                >
                  Save Profile
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="space-y-4">
          <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
            Select Methodology
          </Label>
          <Select value={selectedProfileId} onValueChange={handleProfileChange}>
            <SelectTrigger className="w-full h-14 bg-white/5 border-white/10 text-white rounded-xl">
              <SelectValue placeholder="Choose a profile..." />
            </SelectTrigger>
            <SelectContent className="bg-[#313131] border-white/10 text-white">
              {profiles.length === 0 ? (
                <SelectItem value="none" disabled className="text-slate-400">
                  No profiles found. Save a new config to create one.
                </SelectItem>
              ) : (
                profiles.map((profile) => (
                  <SelectItem key={profile.id} value={profile.id}>
                    <div className="flex flex-col items-start py-1">
                      <span className="font-medium text-white">{profile.name}</span>
                      {profile.description && (
                        <span className="text-xs text-slate-400">{profile.description}</span>
                      )}
                    </div>
                  </SelectItem>
                ))
              )}
            </SelectContent>
          </Select>

          <div className="pt-2 text-xs text-slate-500">
            Selected Profile Configuration: {formData.scanType?.toUpperCase()} | Depth:{' '}
            {formData.maxDepth} | Auth: {formData.authEnabled ? 'On' : 'Off'}
          </div>
        </div>
      </div>

      {/* Step 03: Advanced Configuration */}
      <div className="relative pl-8 ml-3 pb-8 border-l border-white/10">
        <span className="absolute -left-[19px] top-0 flex h-10 w-10 items-center justify-center rounded-full bg-[#313131] border border-white/20 ring-4 ring-[#313131] z-10">
          <span className="text-slate-400 text-sm font-bold font-mono group-hover:text-cyan-400 transition-colors">
            03
          </span>
        </span>
        <h3 className="text-xl font-bold text-white mb-6">Configuration</h3>

        <div className="space-y-8">
          {/* Scheduler Settings */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <Label className="text-white text-sm font-medium">Scheduled Scan</Label>
                <p className="text-slate-500 text-xs mt-1">
                  Automatically run this scan periodically.
                </p>
              </div>
              <Switch
                checked={formData.isScheduled}
                onCheckedChange={(c) => setFormData({ ...formData, isScheduled: c })}
              />
            </div>

            {formData.isScheduled && (
              <div className="space-y-2 animate-in fade-in slide-in-from-top-2">
                <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
                  Frequency
                </Label>
                <Select
                  defaultValue="daily"
                  onValueChange={(v: string) => {
                    const cronMap: any = {
                      daily: '0 0 * * *',
                      weekly: '0 0 * * 1', // Weekly on Monday
                      monthly: '0 0 1 * *', // 1st of month
                    };
                    setFormData({ ...formData, scheduleCron: cronMap[v] || '0 0 * * *' });
                  }}
                >
                  <SelectTrigger className="w-full h-12 bg-white/5 border-white/10 text-white rounded-xl">
                    <SelectValue>Daily (Midnight)</SelectValue>
                  </SelectTrigger>
                  <SelectContent className="bg-[#313131] border-white/10 text-white">
                    <SelectItem value="daily">Daily (Midnight)</SelectItem>
                    <SelectItem value="weekly">Weekly (Monday)</SelectItem>
                    <SelectItem value="monthly">Monthly (1st)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          {/* Steps 04: Advanced Options */}
          <Accordion type="single" collapsible className="w-full border-t border-white/10">
            <AccordionItem value="advanced" className="border-none">
              <AccordionTrigger className="hover:no-underline py-6">
                <div className="flex items-center gap-3">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white/5 border border-white/10">
                    <Settings2 className="h-4 w-4 text-cyan-400" />
                  </span>
                  <span className="text-lg font-bold text-white">Advanced Configuration</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="space-y-8 px-1">
                {/* Authentication */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Lock className="h-4 w-4 text-slate-400" />
                    <h4 className="text-white font-medium">Authenticated Scanning</h4>
                  </div>
                  <div className="flex items-center justify-between bg-white/5 p-4 rounded-xl border border-white/10">
                    <div className="space-y-1">
                      <Label className="text-white">Enable Authentication</Label>
                      <p className="text-xs text-slate-500">
                        Provide credentials for internal scans.
                      </p>
                    </div>
                    <Switch
                      checked={formData.authEnabled}
                      onCheckedChange={(c) => setFormData({ ...formData, authEnabled: c })}
                    />
                  </div>
                  {formData.authEnabled && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2">
                      <div className="space-y-2">
                        <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
                          Login URL
                        </Label>
                        <Input
                          className="bg-white/5 border-white/10 text-white font-mono text-sm h-11"
                          placeholder="https://app.example.com/login"
                          value={formData.authLoginUrl}
                          onChange={(e) =>
                            setFormData({ ...formData, authLoginUrl: e.target.value })
                          }
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
                          Username
                        </Label>
                        <Input
                          className="bg-white/5 border-white/10 text-white font-mono text-sm h-11"
                          placeholder="admin@example.com"
                          value={formData.authUsername}
                          onChange={(e) =>
                            setFormData({ ...formData, authUsername: e.target.value })
                          }
                        />
                      </div>
                      <div className="space-y-2 md:col-span-2">
                        <Label className="text-slate-400 text-xs uppercase tracking-wider font-mono">
                          Password
                        </Label>
                        <Input
                          type="password"
                          className="bg-white/5 border-white/10 text-white font-mono text-sm h-11"
                          placeholder="••••••••••••"
                          value={formData.authPassword}
                          onChange={(e) =>
                            setFormData({ ...formData, authPassword: e.target.value })
                          }
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Attack Vectors */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="h-4 w-4 text-slate-400" />
                    <h4 className="text-white font-medium">Attack Vectors</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3">
                        <Database className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm text-slate-300">SQL Injection</span>
                      </div>
                      <Checkbox
                        checked={formData.vectorSQLi}
                        onCheckedChange={(c: boolean | 'indeterminate') =>
                          setFormData({ ...formData, vectorSQLi: !!c })
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3">
                        <Code2 className="h-4 w-4 text-blue-500" />
                        <span className="text-sm text-slate-300">XSS (Reflected)</span>
                      </div>
                      <Checkbox
                        checked={formData.vectorXSS}
                        onCheckedChange={(c: boolean | 'indeterminate') =>
                          setFormData({ ...formData, vectorXSS: !!c })
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3">
                        <Server className="h-4 w-4 text-purple-500" />
                        <span className="text-sm text-slate-300">SSRF</span>
                      </div>
                      <Checkbox
                        checked={formData.vectorSSRF}
                        onCheckedChange={(c: boolean | 'indeterminate') =>
                          setFormData({ ...formData, vectorSSRF: !!c })
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3">
                        <ShieldAlert className="h-4 w-4 text-red-500" />
                        <span className="text-sm text-slate-300">Misconfigurations</span>
                      </div>
                      <Checkbox
                        checked={formData.vectorMisconfig}
                        onCheckedChange={(c: boolean | 'indeterminate') =>
                          setFormData({ ...formData, vectorMisconfig: !!c })
                        }
                      />
                    </div>
                  </div>
                </div>

                {/* Performance */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="h-4 w-4 text-slate-400" />
                    <h4 className="text-white font-medium">Performance Control</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <Label className="text-slate-400 text-xs uppercase">Rate Limit</Label>
                        <span className="text-xs text-white bg-white/10 px-2 py-0.5 rounded">
                          {formData.rateLimit} req/sec
                        </span>
                      </div>
                      <Slider
                        value={[formData.rateLimit]}
                        max={100}
                        step={1}
                        onValueChange={(v) => setFormData({ ...formData, rateLimit: v[0] })}
                      />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <Label className="text-slate-400 text-xs uppercase">Concurrency</Label>
                        <span className="text-xs text-white bg-white/10 px-2 py-0.5 rounded">
                          {formData.concurrency} threads
                        </span>
                      </div>
                      <Slider
                        value={[formData.concurrency]}
                        max={20}
                        step={1}
                        onValueChange={(v) => setFormData({ ...formData, concurrency: v[0] })}
                      />
                    </div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </div>

      <div className="mt-12 pt-8 border-t border-white/10 flex justify-end items-center gap-4">
        <Button
          variant="ghost"
          className="text-slate-400 hover:text-white hover:bg-white/5 h-12 px-6 rounded-xl"
        >
          Cancel
        </Button>
        <Button
          onClick={handleStartScan}
          disabled={loading}
          className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold h-12 px-8 rounded-xl shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_30px_rgba(6,182,212,0.5)] transition-all"
        >
          <Rocket className="mr-2 h-5 w-5" />
          {loading ? 'Starting...' : 'Start Assessment'}
        </Button>
      </div>
    </div>
  );
}
