import { SettingsShell } from '@/components/settings/settings-shell';

export default function SettingsPage() {
  return (
    <div className="space-y-8 pb-20 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Settings & Preferences</h1>
          <p className="text-slate-400 text-lg font-light mt-2">
            Manage your account, security, and workspace configurations.
          </p>
        </div>
      </div>

      <SettingsShell />
    </div>
  );
}
