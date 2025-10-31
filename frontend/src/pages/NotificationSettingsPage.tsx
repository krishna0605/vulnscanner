import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const NotificationSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [slackAlerts, setSlackAlerts] = useState(false);
  const [pushAlerts, setPushAlerts] = useState(true);

  return (
    <div className="min-h-screen w-full bg-[#0A0B14] text-[#E0E0E0]">
      <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/dashboard')}>
              <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAoGb6izEyw_X-IY8P4G1a15e7o30ltLXJVnqKuWW_bw3qlnzlNNTYrEnkZXhnNLOZHJAuVURDsIy0yKJ7KWbV5ulHg8NFsUL2QIoXSgs3tLTs46S3zXpP3WpI1co60H8nXr7VC9fJbj0cdMT5dL9n4F2bRQo20AdUqCu9h7m8G7YlLEnUZVXjv39K5ticnvVqwC6wCVyIQxyYAJcZ9UhO93dRoTmg_8WKC7IOoAhK-PraBlN-2I9Qr5IK5rlI__qB-QTLv_Fmr4eNx")' }} />
              <div className="flex flex-col"><h1 className="text-[#E0E0E0] text-base font-bold leading-normal">VulnScanner</h1></div>
            </div>
            <nav className="hidden md:flex items-center gap-4">
              <Link to="/dashboard" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-white"><span className="material-symbols-outlined text-base">dashboard</span>Dashboard</Link>
              <Link to="/projects" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#888888]"><span className="material-symbols-outlined text-base">folder</span>Projects</Link>
              <Link to="/scans" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#888888]"><span className="material-symbols-outlined text-base">radar</span>Scans</Link>
              <Link to="/reports" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#888888]"><span className="material-symbols-outlined text-base">bar_chart</span>Reports</Link>
              <Link to="/settings" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#00FFFF]"><span className="material-symbols-outlined text-base">settings</span>Settings</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="px-4 sm:px-10 flex flex-1 justify-center py-8">
        <div className="max-w-7xl w-full flex flex-col gap-8">
          {/* Main */}
          <section className="space-y-6">
            {/* Sub-navbar for settings sections */}
            <div className="relative border-b border-[#2E2E3F] flex gap-6 md:gap-8 px-1">
              <Link to="/settings" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">General</Link>
              <Link to="/settings/api" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">API</Link>
              <span className="relative px-2 py-4 text-sm font-semibold text-[#4A90E2]">Notifications</span>
              <Link to="/settings/security" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">Security</Link>
              <div className="absolute bottom-0 left-[168px] h-0.5 w-24 bg-[#4A90E2] shadow-[0_0_10px_#4A90E2]" />
            </div>
            <div className="rounded-xl bg-[#1A1B23] border border-white/10 p-6">
              <h1 className="text-white text-2xl font-bold">Notification Preferences</h1>
              <p className="text-white/70 mt-1 text-sm">Control how and when you receive alerts.</p>
            </div>
            <div className="rounded-xl bg-[#1A1B23] border border-white/10 p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Email Alerts</p>
                  <p className="text-white/70 text-sm">Critical findings and scan summaries</p>
                </div>
                <label className="inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" checked={emailAlerts} onChange={() => setEmailAlerts(v => !v)} />
                  <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:bg-[#00BFFF] transition-colors"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Slack Notifications</p>
                  <p className="text-white/70 text-sm">Channel updates for team visibility</p>
                </div>
                <label className="inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" checked={slackAlerts} onChange={() => setSlackAlerts(v => !v)} />
                  <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:bg-[#00BFFF] transition-colors"></div>
                </label>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Push Notifications</p>
                  <p className="text-white/70 text-sm">In-app alerts for activity and changes</p>
                </div>
                <label className="inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" checked={pushAlerts} onChange={() => setPushAlerts(v => !v)} />
                  <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:bg-[#00BFFF] transition-colors"></div>
                </label>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default NotificationSettingsPage;