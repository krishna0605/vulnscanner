'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  Smartphone,
  Copy,
  Check,
  Eye,
  EyeOff,
  Bell,
  Mail,
  Slack,
  Terminal,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { logger } from '@/utils/logger';

export function ProfileSection() {
  const [displayName, setDisplayName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [bio, setBio] = React.useState('');
  const [avatarUrl, setAvatarUrl] = React.useState<string | null>(null);
  const [saved, setSaved] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [uploading, setUploading] = React.useState(false);
  const [userId, setUserId] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Import Supabase client
  const supabase = React.useMemo(() => {
    // Dynamic import to avoid SSR issues
    const { createClient } = require('@/utils/supabase/client');
    return createClient();
  }, []);

  // Load user session and profile on mount
  React.useEffect(() => {
    async function loadProfile() {
      try {
        // Get user session
        const {
          data: { user },
        } = await supabase.auth.getUser();

        if (user) {
          setUserId(user.id);
          setEmail(user.email || '');

          // Fetch profile from database
          const { data: profile } = await supabase
            .from('profiles')
            .select('full_name, bio, avatar_url')
            .eq('id', user.id)
            .single();

          if (profile) {
            setDisplayName(profile.full_name || '');
            setBio(profile.bio || '');
            setAvatarUrl(profile.avatar_url);
          }
        }
      } catch (error) {
        logger.error('Error loading profile:', { error });
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, [supabase]);

  const handleSave = async () => {
    if (!userId) return;

    try {
      const { error } = await supabase.from('profiles').upsert({
        id: userId,
        full_name: displayName || null,
        bio: bio || null,
        avatar_url: avatarUrl,
        updated_at: new Date().toISOString(),
      });

      if (!error) {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      }
    } catch (error) {
      logger.error('Error saving profile:', { error });
    }
  };

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !userId) return;

    // Check file size (2MB limit)
    if (file.size > 2 * 1024 * 1024) {
      alert('File size must be less than 2MB');
      return;
    }

    setUploading(true);
    try {
      // Delete old avatar first
      const { data: existingFiles } = await supabase.storage.from('avatars').list(userId);

      if (existingFiles && existingFiles.length > 0) {
        const filesToDelete = existingFiles.map((f: any) => `${userId}/${f.name}`);
        await supabase.storage.from('avatars').remove(filesToDelete);
      }

      // Upload new avatar
      const fileExt = file.name.split('.').pop();
      const fileName = `${userId}/avatar.${fileExt}`;

      const { error: uploadError } = await supabase.storage
        .from('avatars')
        .upload(fileName, file, { upsert: true });

      if (!uploadError) {
        const { data: urlData } = supabase.storage.from('avatars').getPublicUrl(fileName);

        // Add cache buster to force refresh
        const newUrl = `${urlData.publicUrl}?t=${Date.now()}`;
        setAvatarUrl(newUrl);
      }
    } catch (error) {
      logger.error('Error uploading avatar:', { error });
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveAvatar = async () => {
    if (!userId) return;

    try {
      const { data: existingFiles } = await supabase.storage.from('avatars').list(userId);

      if (existingFiles && existingFiles.length > 0) {
        const filesToDelete = existingFiles.map((f: any) => `${userId}/${f.name}`);
        await supabase.storage.from('avatars').remove(filesToDelete);
      }

      setAvatarUrl(null);
    } catch (error) {
      logger.error('Error removing avatar:', { error });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">Profile & Account</h2>
        <p className="text-slate-400 text-sm">
          Manage your personal information and workspace details.
        </p>
      </div>

      <div className="flex items-center gap-6 pb-8 border-b border-white/5">
        {/* Avatar - Empty by default, shows image if uploaded */}
        {avatarUrl ? (
          <img
            src={avatarUrl}
            alt="Avatar"
            className="h-20 w-20 rounded-full object-cover shadow-[0_0_20px_rgba(6,182,212,0.3)] ring-4 ring-[#1a1a1a]"
          />
        ) : (
          <div className="h-20 w-20 rounded-full bg-[#252525] border-2 border-dashed border-white/20 flex items-center justify-center text-slate-500 ring-4 ring-[#1a1a1a]">
            {displayName
              ? displayName
                  .split(' ')
                  .map((n) => n[0])
                  .join('')
                  .toUpperCase()
                  .slice(0, 2)
              : '?'}
          </div>
        )}
        <div className="space-y-3">
          <div className="flex gap-3">
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              className="hidden"
              onChange={handleAvatarUpload}
            />
            <Button
              variant="outline"
              size="sm"
              className="h-9 border-white/10 bg-white/5 hover:bg-white/10 text-white"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload New'}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-9 text-red-400 hover:text-red-300 hover:bg-red-500/10"
              onClick={handleRemoveAvatar}
              disabled={!avatarUrl}
            >
              Remove
            </Button>
          </div>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest">Max size 2MB</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label className="text-slate-400 text-xs">Display Name</Label>
          <Input
            className="bg-[#252525] border-white/5 text-white h-11 focus:bg-[#2a2a2a]"
            placeholder="Enter your name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label className="text-slate-400 text-xs">Email Address</Label>
          <Input
            className="bg-[#252525] border-white/5 text-white/60 h-11 cursor-not-allowed"
            value={email}
            disabled
            readOnly
          />
        </div>
        <div className="space-y-2 col-span-2">
          <Label className="text-slate-400 text-xs">Bio / Role</Label>
          <textarea
            className="flex w-full rounded-md border border-white/5 bg-[#252525] px-3 py-2 text-sm text-white placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-cyan-500/50 min-h-[100px] resize-none"
            placeholder="Tell us about yourself..."
            value={bio}
            onChange={(e) => setBio(e.target.value)}
          />
        </div>
      </div>

      {/* Export Data Section */}
      <div className="pt-6 border-t border-white/5">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Export Your Data
        </h3>
        <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
          <div>
            <p className="text-white font-medium text-sm">Download Your Data</p>
            <p className="text-xs text-slate-500">
              Get a copy of all your projects, scans, and findings
            </p>
          </div>
          <Button
            variant="outline"
            className="border-white/10 text-white hover:bg-white/5"
            onClick={async () => {
              if (!userId) return;
              const { exportUserData } = await import('@/lib/profile-api');
              const data = await exportUserData(userId);
              const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `vulnscanner-export-${new Date().toISOString().split('T')[0]}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            <Copy className="h-4 w-4 mr-2" /> Export
          </Button>
        </div>
      </div>

      {/* Account Activity Section */}
      <div className="pt-6 border-t border-white/5">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Account Activity
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-white/5 rounded-lg text-slate-400">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <p className="text-white font-medium text-sm">Last Login</p>
                <p className="text-xs text-slate-500">
                  {new Date().toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
            <div>
              <p className="text-white font-medium text-sm">Sign Out All Devices</p>
              <p className="text-xs text-slate-500">
                This will log you out of all devices including this one
              </p>
            </div>
            <Button
              variant="outline"
              className="border-white/10 text-white hover:bg-white/5"
              onClick={async () => {
                if (confirm('Are you sure you want to sign out of all devices?')) {
                  await supabase.auth.signOut({ scope: 'global' });
                  window.location.href = '/login';
                }
              }}
            >
              Sign Out All
            </Button>
          </div>
        </div>
      </div>

      {/* Danger Zone Section */}
      <div className="pt-6 border-t border-red-500/20">
        <h3 className="text-sm font-bold text-red-400 uppercase tracking-widest mb-4">
          Danger Zone
        </h3>
        <div className="flex items-center justify-between p-4 bg-red-500/5 rounded-xl border border-red-500/20">
          <div>
            <p className="text-white font-medium text-sm">Delete Account</p>
            <p className="text-xs text-slate-500">
              Permanently delete your account and all associated data
            </p>
          </div>
          <Button
            variant="destructive"
            className="bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30"
            onClick={async () => {
              if (!userId) return;

              const confirmText = prompt('Type "DELETE" to confirm account deletion:');
              if (confirmText !== 'DELETE') return;

              const finalConfirm = confirm(
                '⚠️ This action is IRREVERSIBLE. All your projects, scans, and data will be permanently deleted. Are you absolutely sure?'
              );
              if (!finalConfirm) return;

              try {
                // Delete avatar from storage first
                const { data: existingFiles } = await supabase.storage.from('avatars').list(userId);

                if (existingFiles && existingFiles.length > 0) {
                  const filesToDelete = existingFiles.map((f: any) => `${userId}/${f.name}`);
                  await supabase.storage.from('avatars').remove(filesToDelete);
                }

                // Call the delete_user_account RPC function
                const { error } = await supabase.rpc('delete_user_account', {
                  user_id_param: userId,
                });

                if (error) {
                  alert('Error deleting account: ' + error.message);
                  return;
                }

                // Sign out the user
                await supabase.auth.signOut();

                alert('Your account has been deleted. Redirecting to login...');
                window.location.href = '/login';
              } catch (err) {
                logger.error('Delete account error:', { err });
                alert('An error occurred while deleting your account.');
              }
            }}
          >
            Delete Account
          </Button>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <Button
          onClick={handleSave}
          className={`font-bold px-8 shadow-glow transition-all ${saved ? 'bg-emerald-500 text-white' : 'bg-cyan-500 text-black hover:bg-cyan-400'}`}
        >
          {saved ? '✓ Saved!' : 'Save Changes'}
        </Button>
      </div>
    </div>
  );
}

export function SecuritySection() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">Security & Authentication</h2>
        <p className="text-slate-400 text-sm">
          Enhance your account security with 2FA and hardware keys.
        </p>
      </div>

      <div className="bg-gradient-to-br from-emerald-500/5 to-transparent p-6 rounded-xl border border-emerald-500/10 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400">
            <Shield className="h-6 w-6" />
          </div>
          <div>
            <h4 className="text-white font-bold">Two-Factor Authentication</h4>
            <p className="text-xs text-emerald-400/80 mt-1">
              Currently Active via Authenticator App
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          className="border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/10 hover:text-emerald-300"
        >
          Configure
        </Button>
      </div>

      <div className="space-y-6">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mt-8 mb-4">
          Password Management
        </h3>
        <div className="grid grid-cols-1 gap-4 max-w-lg">
          <div className="space-y-2">
            <Label className="text-slate-400 text-xs">Current Password</Label>
            <Input type="password" className="bg-[#252525] border-white/5 text-white" />
          </div>
          <div className="space-y-2">
            <Label className="text-slate-400 text-xs">New Password</Label>
            <Input type="password" className="bg-[#252525] border-white/5 text-white" />
          </div>
        </div>
        <Button disabled className="bg-white/5 text-slate-500">
          Update Password
        </Button>
      </div>
    </div>
  );
}

export function NotificationsSection() {
  const [settings, setSettings] = React.useState({
    criticalVulns: true,
    scanCompletions: true,
    weeklyReports: true,
  });

  // Load from localStorage on mount
  React.useEffect(() => {
    const saved = localStorage.getItem('vulnscanner_notifications');
    if (saved) {
      setSettings(JSON.parse(saved));
    }
  }, []);

  const updateSetting = (key: keyof typeof settings, value: boolean) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    localStorage.setItem('vulnscanner_notifications', JSON.stringify(newSettings));
  };

  const notificationItems = [
    {
      key: 'criticalVulns' as const,
      title: 'Critical Vulnerabilities',
      desc: 'Immediate alerts when high-risk issues are found.',
      icon: Shield,
    },
    {
      key: 'scanCompletions' as const,
      title: 'Scan Completions',
      desc: 'Notify when a scheduled scan finishes.',
      icon: Terminal,
    },
    {
      key: 'weeklyReports' as const,
      title: 'Weekly Reports',
      desc: 'Receive a summary PDF of all activity.',
      icon: Mail,
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">Notifications</h2>
        <p className="text-slate-400 text-sm">Choose how and when you want to be alerted.</p>
      </div>

      <div className="space-y-6">
        {notificationItems.map((item, i) => (
          <div
            key={i}
            className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5"
          >
            <div className="flex items-center gap-4">
              <div className="p-2 bg-white/5 rounded-lg text-slate-400">
                <item.icon className="h-5 w-5" />
              </div>
              <div>
                <h4 className="text-white font-medium text-sm">{item.title}</h4>
                <p className="text-xs text-slate-500">{item.desc}</p>
              </div>
            </div>
            <Switch
              checked={settings[item.key]}
              onCheckedChange={(checked) => updateSetting(item.key, checked)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ApiSection() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">API & Integrations</h2>
        <p className="text-slate-400 text-sm">Manage API keys and external tool connections.</p>
      </div>

      <div className="bg-[#1a1a1a] p-6 rounded-xl border border-white/10 space-y-4">
        <div className="flex justify-between items-center">
          <Label className="text-slate-400 text-xs uppercase tracking-wider">
            Production API Key
          </Label>
          <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            Active
          </span>
        </div>
        <div className="flex gap-3">
          <div className="flex-1 bg-black/50 rounded-lg border border-white/5 p-3 font-mono text-xs text-slate-300 flex items-center justify-between">
            <span>sk_live_51Mz...9x2A</span>
            <div className="flex gap-2">
              <Button
                size="icon"
                variant="ghost"
                className="h-6 w-6 text-slate-500 hover:text-white"
              >
                <EyeOff className="h-3 w-3" />
              </Button>
            </div>
          </div>
          <Button variant="outline" className="border-white/10 text-white hover:bg-white/5">
            <Copy className="h-4 w-4 mr-2" /> Copy
          </Button>
        </div>
        <p className="text-[10px] text-slate-500">
          Last used 2 hours ago by &quot;CI/CD Pipeline&quot;
        </p>
      </div>

      <div>
        <h3 className="text-sm font-bold text-white mb-4">Connected Properties</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-white/10 rounded-xl bg-white/5 flex items-center justify-between opacity-50 cursor-not-allowed">
            <div className="flex items-center gap-3">
              <Slack className="h-5 w-5 text-slate-400" />
              <span className="text-slate-400 font-medium">Slack</span>
            </div>
            <span className="text-[10px] text-slate-600 border border-slate-700 px-2 py-1 rounded">
              Coming Soon
            </span>
          </div>
          <div className="p-4 border border-white/10 rounded-xl bg-white/5 flex items-center justify-between opacity-50 cursor-not-allowed">
            <div className="flex items-center gap-3">
              <Shield className="h-5 w-5 text-slate-400" />
              <span className="text-slate-400 font-medium">Jira</span>
            </div>
            <span className="text-[10px] text-slate-600 border border-slate-700 px-2 py-1 rounded">
              Coming Soon
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
