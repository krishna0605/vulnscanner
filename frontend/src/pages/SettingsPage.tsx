import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen w-full bg-[#0A0B14] text-[#E0E0E0]">
      {/* Header */}
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
              <span className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#00FFFF]"><span className="material-symbols-outlined text-base">settings</span>Settings</span>
            </nav>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="px-4 sm:px-10 flex flex-1 justify-center py-8">
        <div className="max-w-7xl w-full flex flex-col gap-8">
          {/* Main panel */}
          <section className="space-y-6">
            {/* Sub-navbar for settings sections */}
            <div className="relative border-b border-[#2E2E3F] flex gap-6 md:gap-8 px-1">
              <span className="relative px-2 py-4 text-sm font-semibold text-[#4A90E2]">General</span>
              <Link to="/settings/api" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">API</Link>
              <Link to="/settings/notifications" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">Notifications</Link>
              <Link to="/settings/security" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">Security</Link>
              <div className="absolute bottom-0 left-2 h-0.5 w-16 bg-[#4A90E2] shadow-[0_0_10px_#4A90E2]" />
            </div>

            {/* General settings content */}
            <div className="rounded-xl bg-[#1A1B23] border border-white/10 p-6 space-y-4">
              <h1 className="text-white text-2xl font-bold">General Settings</h1>
              <p className="text-white/70 text-sm">Configure your basic preferences, appearance, and localization.</p>
            </div>

            <div className="rounded-xl bg-[#1A1B23] border border-white/10 p-6 space-y-6">
              {/* Profile preferences */}
              <div className="space-y-3">
                <h2 className="text-white text-lg font-bold">Profile</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex flex-col gap-2">
                    <span className="text-sm text-white/70">Display Name</span>
                    <input className="rounded-lg bg-[#131523]/80 border border-[#2E2E3F] px-3 py-2 text-sm text-white placeholder:text-[#888888]" placeholder="Jane Admin" />
                  </label>
                  <label className="flex flex-col gap-2">
                    <span className="text-sm text-white/70">Email</span>
                    <input className="rounded-lg bg-[#131523]/80 border border-[#2E2E3F] px-3 py-2 text-sm text-white placeholder:text-[#888888]" placeholder="jane@example.com" />
                  </label>
                </div>
              </div>

              {/* Appearance */}
              <div className="space-y-3">
                <h2 className="text-white text-lg font-bold">Appearance</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex flex-col gap-2">
                    <span className="text-sm text-white/70">Theme</span>
                    <select className="rounded-lg bg-[#131523]/80 border border-[#2E2E3F] px-3 py-2 text-sm text-white">
                      <option>Dark</option>
                      <option>Light</option>
                    </select>
                  </label>
                  <label className="flex flex-col gap-2">
                    <span className="text-sm text-white/70">Density</span>
                    <select className="rounded-lg bg-[#131523]/80 border border-[#2E2E3F] px-3 py-2 text-sm text-white">
                      <option>Comfortable</option>
                      <option>Compact</option>
                    </select>
                  </label>
                </div>
              </div>

              {/* Localization */}
              <div className="space-y-3">
                <h2 className="text-white text-lg font-bold">Localization</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex flex-col gap-2">
                    <span className="text-sm text-white/70">Language</span>
                    <select className="rounded-lg bg-[#131523]/80 border border-[#2E2E3F] px-3 py-2 text-sm text-white">
                      <option>English</option>
                      <option>French</option>
                      <option>German</option>
                    </select>
                  </label>
                  <label className="flex flex-col gap-2">
                    <span className="text-sm text-white/70">Timezone</span>
                    <select className="rounded-lg bg-[#131523]/80 border border-[#2E2E3F] px-3 py-2 text-sm text-white">
                      <option>UTC</option>
                      <option>Local</option>
                    </select>
                  </label>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;