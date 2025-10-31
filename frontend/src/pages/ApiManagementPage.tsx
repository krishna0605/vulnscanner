import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

type ApiKey = { id: string; name: string; created: string; lastUsed?: string; scopes: string[] };

const initialKeys: ApiKey[] = [
  { id: 'pk_live_1A2B3C', name: 'CI/CD Pipeline', created: '2024-06-14', lastUsed: '2024-10-20', scopes: ['scans:read', 'projects:read'] },
  { id: 'pk_live_4D5E6F', name: 'Security Dashboard', created: '2024-07-03', scopes: ['findings:read', 'reports:read'] },
];

const ApiManagementPage: React.FC = () => {
  const navigate = useNavigate();
  const [keys, setKeys] = useState<ApiKey[]>(initialKeys);
  const [name, setName] = useState('');
  const [scope, setScope] = useState('scans:read');

  const addKey = () => {
    if (!name.trim()) return;
    const id = 'pk_live_' + Math.random().toString(36).slice(2, 8).toUpperCase();
    const newKey: ApiKey = { id, name, created: new Date().toISOString().slice(0, 10), scopes: [scope] };
    setKeys((prev) => [newKey, ...prev]);
    setName('');
  };

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
          {/* Breadcrumbs */}
          <div className="flex flex-wrap gap-2" aria-label="Breadcrumb">
            <Link to="/dashboard" className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Dashboard</Link>
            <span className="text-[#9da1b8] text-sm">/</span>
            <Link to="/settings" className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Settings</Link>
            <span className="text-[#9da1b8] text-sm">/</span>
            <span className="text-white text-sm">API Management</span>
          </div>

          <div className="flex flex-col gap-8">
            {/* Main */}
            <section className="space-y-6">
              {/* Sub-navbar for settings sections */}
              <div className="relative border-b border-[#2E2E3F] flex gap-6 md:gap-8 px-1">
                <Link to="/settings" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">General</Link>
                <span className="relative px-2 py-4 text-sm font-semibold text-[#4A90E2]">API</span>
                <Link to="/settings/notifications" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">Notifications</Link>
                <Link to="/settings/security" className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">Security</Link>
                <div className="absolute bottom-0 left-[84px] h-0.5 w-10 bg-[#4A90E2] shadow-[0_0_10px_#4A90E2]" />
              </div>
              <div className="rounded-xl bg-[#1A1B23] border border-white/10 p-6">
                <h1 className="text-white text-2xl font-bold">API Keys</h1>
                <p className="text-white/70 mt-1 text-sm">Create keys, manage scopes, and revoke access.</p>
              </div>
              <div className="rounded-xl bg-[#1A1B23] border border-white/10 p-6 space-y-4">
                <div className="flex flex-wrap items-center gap-3">
                  <input className="bg-[#0A0B14] border border-white/10 rounded-lg h-9 px-3 text-sm w-64" placeholder="Key name (e.g., CI Pipeline)" value={name} onChange={(e) => setName(e.target.value)} />
                  <select className="bg-[#0A0B14] border border-white/10 rounded-lg h-9 px-3 text-sm" value={scope} onChange={(e) => setScope(e.target.value)}>
                    <option value="scans:read">scans:read</option>
                    <option value="projects:read">projects:read</option>
                    <option value="findings:read">findings:read</option>
                    <option value="reports:read">reports:read</option>
                  </select>
                  <button className="rounded-lg h-9 px-4 bg-[#00FFFF] text-black text-sm font-bold" onClick={addKey}>Generate Key</button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-white/70">
                        <th className="py-2">Name</th>
                        <th className="py-2">Key</th>
                        <th className="py-2">Scopes</th>
                        <th className="py-2">Created</th>
                        <th className="py-2">Last Used</th>
                        <th className="py-2 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {keys.map((k) => (
                        <tr key={k.id} className="border-t border-white/10">
                          <td className="py-2 font-medium">{k.name}</td>
                          <td className="py-2 font-mono text-[#00E5FF]">{k.id}</td>
                          <td className="py-2">{k.scopes.join(', ')}</td>
                          <td className="py-2">{k.created}</td>
                          <td className="py-2">{k.lastUsed || '—'}</td>
                          <td className="py-2 text-right">
                            <button className="inline-flex items-center rounded-lg px-3 py-1 text-xs font-medium bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">Revoke</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ApiManagementPage;