'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Bell, Shield, Key, CreditCard, Monitor } from 'lucide-react';
import { cn } from '@/lib/utils';
// Import individual sections
import {
  ProfileSection,
  SecuritySection,
  NotificationsSection,
  ApiSection,
} from './settings-sections';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';

interface SettingsShellProps {
  children?: React.ReactNode;
}

const TABS = [
  { id: 'profile', label: 'Profile & Account', icon: User },
  { id: 'security', label: 'Security & 2FA', icon: Shield },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'api', label: 'API & Integrations', icon: Key },
  { id: 'billing', label: 'Plan & Billing', icon: CreditCard },
  { id: 'system', label: 'System Preferences', icon: Monitor },
];

export function SettingsShell() {
  const [activeTab, setActiveTab] = React.useState('profile');

  return (
    <div className="flex flex-col lg:flex-row gap-8 min-h-[600px]">
      {/* Sidebar Navigation */}
      <div className="lg:w-64 flex-shrink-0 space-y-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 relative overflow-hidden group',
              activeTab === tab.id
                ? 'bg-white/10 text-white shadow-lg border border-white/5'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            )}
          >
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-transparent opacity-50"
                initial={false}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
            <tab.icon
              className={cn(
                'h-4 w-4 z-10',
                activeTab === tab.id
                  ? 'text-cyan-400'
                  : 'text-slate-500 group-hover:text-cyan-400 transition-colors'
              )}
            />
            <span className="text-sm font-medium z-10">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="flex-1 glass-panel p-8 rounded-[24px] border border-white/10 relative overflow-hidden min-h-[600px]">
        {/* Decorative Background Elements */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-cyan-500/5 rounded-full blur-[100px] pointer-events-none -translate-y-1/2 translate-x-1/2" />

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
            className="relative z-10"
          >
            {activeTab === 'profile' && <ProfileSection />}
            {activeTab === 'security' && <SecuritySection />}
            {activeTab === 'notifications' && <NotificationsSection />}
            {activeTab === 'api' && <ApiSection />}
            {activeTab === 'billing' && <BillingSection />}
            {activeTab === 'system' && <SystemSection />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

function BillingSection() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">Plan & Billing</h2>
        <p className="text-slate-400 text-sm">Manage your subscription and view usage analytics.</p>
      </div>

      {/* Current Plan Card */}
      <div className="bg-gradient-to-br from-cyan-500/10 to-blue-600/10 p-6 rounded-xl border border-cyan-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="relative z-10">
          <div className="flex justify-between items-start mb-4">
            <div>
              <span className="text-[10px] text-cyan-400 uppercase tracking-widest font-bold">
                Current Plan
              </span>
              <h3 className="text-2xl font-bold text-white mt-1">Professional</h3>
            </div>
            <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-bold rounded-full border border-emerald-500/20">
              Active
            </span>
          </div>
          <p className="text-slate-400 text-sm mb-4">
            Unlimited scans, 10 projects, priority support
          </p>
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
            >
              Upgrade Plan
            </Button>
            <Button variant="ghost" className="text-slate-400 hover:text-white">
              View All Plans
            </Button>
          </div>
        </div>
      </div>

      {/* Usage Stats */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Usage This Month
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/5 p-4 rounded-xl border border-white/5">
            <div className="flex justify-between items-center mb-2">
              <span className="text-slate-400 text-xs">Scans Used</span>
              <span className="text-white font-mono text-sm">45 / ∞</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-cyan-500 rounded-full w-[45%]" />
            </div>
          </div>
          <div className="bg-white/5 p-4 rounded-xl border border-white/5">
            <div className="flex justify-between items-center mb-2">
              <span className="text-slate-400 text-xs">Projects</span>
              <span className="text-white font-mono text-sm">3 / 10</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-violet-500 rounded-full w-[30%]" />
            </div>
          </div>
          <div className="bg-white/5 p-4 rounded-xl border border-white/5">
            <div className="flex justify-between items-center mb-2">
              <span className="text-slate-400 text-xs">API Calls</span>
              <span className="text-white font-mono text-sm">1.2K / 10K</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full w-[12%]" />
            </div>
          </div>
        </div>
      </div>

      {/* Payment Method */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Payment Method
        </h3>
        <div className="bg-white/5 p-4 rounded-xl border border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-2 bg-white/10 rounded-lg">
              <CreditCard className="h-5 w-5 text-slate-300" />
            </div>
            <div>
              <p className="text-white font-medium">•••• •••• •••• 4242</p>
              <p className="text-xs text-slate-500">Expires 12/26</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" className="text-slate-400 hover:text-white">
            Update
          </Button>
        </div>
      </div>

      {/* Billing History */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Recent Invoices
        </h3>
        <div className="space-y-2">
          {[
            { date: 'Jan 1, 2026', amount: '$49.00', status: 'Paid' },
            { date: 'Dec 1, 2025', amount: '$49.00', status: 'Paid' },
            { date: 'Nov 1, 2025', amount: '$49.00', status: 'Paid' },
          ].map((invoice, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 bg-white/[0.02] rounded-lg hover:bg-white/5 transition-colors"
            >
              <div className="flex items-center gap-4">
                <span className="text-slate-400 text-sm font-mono">{invoice.date}</span>
                <span className="text-white font-medium">{invoice.amount}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-emerald-400 text-xs">{invoice.status}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-slate-500 hover:text-white text-xs"
                >
                  Download
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SystemSection() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">System Preferences</h2>
        <p className="text-slate-400 text-sm">
          Customize your workspace experience and global settings.
        </p>
      </div>

      {/* Appearance */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Appearance
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <button className="p-4 bg-white/5 rounded-xl border-2 border-cyan-500/50 flex flex-col items-center gap-2 hover:bg-white/10 transition-colors">
            <div className="w-full h-12 bg-[#1a1a1a] rounded-lg border border-white/10" />
            <span className="text-white text-xs font-medium">Dark</span>
          </button>
          <button className="p-4 bg-white/5 rounded-xl border border-white/10 flex flex-col items-center gap-2 hover:bg-white/10 transition-colors opacity-50">
            <div className="w-full h-12 bg-slate-200 rounded-lg" />
            <span className="text-slate-400 text-xs font-medium">Light</span>
          </button>
          <button className="p-4 bg-white/5 rounded-xl border border-white/10 flex flex-col items-center gap-2 hover:bg-white/10 transition-colors opacity-50">
            <div className="w-full h-12 bg-gradient-to-r from-[#1a1a1a] to-slate-200 rounded-lg" />
            <span className="text-slate-400 text-xs font-medium">System</span>
          </button>
        </div>
      </div>

      {/* Language & Region */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Language & Region
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs text-slate-400">Language</label>
            <select className="w-full bg-[#252525] border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500/50">
              <option>English (US)</option>
              <option>English (UK)</option>
              <option>Spanish</option>
              <option>French</option>
              <option>German</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs text-slate-400">Timezone</label>
            <select className="w-full bg-[#252525] border border-white/10 rounded-lg p-3 text-white text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500/50">
              <option>UTC +5:30 (IST)</option>
              <option>UTC +0:00 (GMT)</option>
              <option>UTC -5:00 (EST)</option>
              <option>UTC -8:00 (PST)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Data & Privacy */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
          Data & Privacy
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
            <div>
              <p className="text-white font-medium text-sm">Analytics Collection</p>
              <p className="text-xs text-slate-500">
                Help improve VulnScanner by sending anonymous usage data
              </p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
            <div>
              <p className="text-white font-medium text-sm">Auto-delete Old Scans</p>
              <p className="text-xs text-slate-500">
                Automatically remove scan data older than 90 days
              </p>
            </div>
            <Switch />
          </div>
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
            <div>
              <p className="text-white font-medium text-sm">Session Timeout</p>
              <p className="text-xs text-slate-500">Auto-logout after 30 minutes of inactivity</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div>
        <h3 className="text-sm font-bold text-red-400 uppercase tracking-widest mb-4">
          Danger Zone
        </h3>
        <div className="p-4 bg-red-500/5 rounded-xl border border-red-500/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-medium text-sm">Delete All Data</p>
              <p className="text-xs text-slate-500">
                Permanently delete all projects, scans, and findings
              </p>
            </div>
            <Button
              variant="outline"
              className="border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
            >
              Delete Everything
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
