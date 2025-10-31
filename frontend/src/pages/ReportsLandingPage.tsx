import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

type SeveritySummary = { critical: number; high: number; medium: number; low: number };
type Project = { id: number; name: string; owner?: string; createdAt?: string };
type Scan = {
  id: number;
  target: string;
  date: string;
  status: 'Completed' | 'Warnings' | 'Critical Found' | 'Cancelled' | 'Running';
  severity: SeveritySummary;
  projectId: number | null;
};

const mockProjects: Project[] = [
  { id: 1, name: 'Project Phoenix', owner: 'CyberCorp', createdAt: '2023-10-01' },
  { id: 2, name: 'E-Commerce Platform', owner: 'ShopCo', createdAt: '2023-09-12' },
];

const mockScans: Scan[] = [
  {
    id: 101,
    target: 'example.com',
    date: '2023-10-26 14:30',
    status: 'Completed',
    severity: { critical: 5, high: 15, medium: 22, low: 8 },
    projectId: 1,
  },
  {
    id: 102,
    target: 'secure-api.dev',
    date: '2023-10-25 09:15',
    status: 'Critical Found',
    severity: { critical: 5, high: 12, medium: 18, low: 4 },
    projectId: null,
  },
  {
    id: 103,
    target: 'e-commerce-store.com',
    date: '2023-10-24 22:00',
    status: 'Warnings',
    severity: { critical: 0, high: 8, medium: 22, low: 11 },
    projectId: 2,
  },
  {
    id: 104,
    target: 'test-env.internal',
    date: '2023-10-23 11:45',
    status: 'Cancelled',
    severity: { critical: 0, high: 0, medium: 0, low: 0 },
    projectId: null,
  },
];

const ReportsLandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<'All' | 'Critical' | 'High' | 'Medium' | 'Low'>('All');
  const [statusFilter, setStatusFilter] = useState<'All' | Scan['status']>('All');
  const [typeFilter, setTypeFilter] = useState<'All' | 'Project' | 'Individual'>('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 400);
    return () => clearTimeout(t);
  }, []);

  const filteredScans = useMemo(() => {
    return mockScans.filter((scan) => {
      const matchesQuery =
        !query || scan.target.toLowerCase().includes(query.toLowerCase());
      const matchesSeverity =
        severityFilter === 'All' ||
        (severityFilter === 'Critical' && scan.severity.critical > 0) ||
        (severityFilter === 'High' && scan.severity.high > 0) ||
        (severityFilter === 'Medium' && scan.severity.medium > 0) ||
        (severityFilter === 'Low' && scan.severity.low > 0);
      const matchesStatus = statusFilter === 'All' || scan.status === statusFilter;
      const matchesType =
        typeFilter === 'All' ||
        (typeFilter === 'Project' && scan.projectId !== null) ||
        (typeFilter === 'Individual' && scan.projectId === null);
      return matchesQuery && matchesSeverity && matchesStatus && matchesType;
    });
  }, [query, severityFilter, statusFilter, typeFilter]);

  const onRowActivate = (scan: Scan) => {
    if (scan.projectId) {
      navigate(`/reports/project/${scan.projectId}`);
    } else {
      navigate(`/reports/scan/${scan.id}`);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#0A0B14] text-[#E0E0E0]">
      {/* Top navbar */}
      <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/dashboard')}>
              <div
                className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9"
                style={{
                  backgroundImage:
                    'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAoGb6izEyw_X-IY8P4G1a15e7o30ltLXJVnqKuWW_bw3qlnzlNNTYrEnkZXhnNLOZHJAuVURDsIy0yKJ7KWbV5ulHg8NFsUL2QIoXSgs3tLTs46S3zXpP3WpI1co60H8nXr7VC9fJbj0cdMT5dL9n4F2bRQo20AdUqCu9h7m8G7YlLEnUZVXjv39K5ticnvVqwC6wCVyIQxyYAJcZ9UhO93dRoTmg_8WKC7IOoAhK-PraBlN-2I9Qr5IK5rlI__qB-QTLv_Fmr4eNx")',
                }}
              />
              <div className="flex flex-col">
                <h1 className="text-[#E0E0E0] text-base font-bold leading-normal">VulnScanner</h1>
              </div>
            </div>
            <nav className="hidden md:flex items-center gap-4">
              <Link to="/dashboard" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-white transition-all"><span className="material-symbols-outlined text-base">dashboard</span>Dashboard</Link>
              <Link to="/projects" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#888888] transition-all"><span className="material-symbols-outlined text-base">folder</span>Projects</Link>
              <Link to="/scans" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#888888] transition-all"><span className="material-symbols-outlined text-base">radar</span>Scans</Link>
              <span className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#00FFFF] transition-all"><span className="material-symbols-outlined text-base">bar_chart</span>Reports</span>
            </nav>
          </div>
          <div className="flex items-center gap-2 sm:gap-4">
            <div className="relative w-full md:w-72">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#888888]">search</span>
              <input
                className="bg-[#131523]/80 border border-[#2E2E3F]/50 text-white text-sm rounded-lg focus:ring-[#00FFFF] focus:border-[#00FFFF] block w-full pl-10 p-2.5 transition-colors h-10"
                placeholder="Search projects or scans..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                aria-label="Search projects or scans"
              />
            </div>
            <button className="flex min-w-[120px] items-center justify-center rounded-lg h-10 px-4 bg-[#00FFFF] text-black text-sm font-bold hover:shadow-[0_0_10px_rgba(0,255,255,0.5)] transition-shadow" onClick={() => navigate('/scans/new')} title="Configure a new scan">
              <span className="material-symbols-outlined mr-2 text-base">play_arrow</span>
              New Scan
            </button>
          </div>
        </div>
      </header>

      <main className="px-4 sm:px-10 flex flex-1 justify-center py-8">
        <div className="flex flex-col w-full max-w-7xl gap-6">
          {/* Breadcrumbs */}
          <div className="flex flex-wrap gap-2" aria-label="Breadcrumb">
            <Link to="/dashboard" className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Dashboard</Link>
            <span className="text-[#9da1b8] text-sm">/</span>
            <span className="text-white text-sm">Reports</span>
          </div>

          {/* Toolbar & Filters */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 p-4 bg-[#131523] rounded-lg border border-[#2E2E3F]/50">
            <div className="flex items-center gap-2 flex-wrap">
              <div className="flex items-center gap-2">
                <label className="text-white text-sm">Severity</label>
                <select
                  className="bg-[#0A0B14] border border-white/10 text-white text-sm rounded-lg h-9 px-3"
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value as any)}
                  aria-label="Filter by severity"
                >
                  <option>All</option>
                  <option>Critical</option>
                  <option>High</option>
                  <option>Medium</option>
                  <option>Low</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-white text-sm">Status</label>
                <select
                  className="bg-[#0A0B14] border border-white/10 text-white text-sm rounded-lg h-9 px-3"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as any)}
                  aria-label="Filter by status"
                >
                  <option>All</option>
                  <option>Completed</option>
                  <option>Warnings</option>
                  <option>Critical Found</option>
                  <option>Cancelled</option>
                  <option>Running</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-white text-sm">Type</label>
                <select
                  className="bg-[#0A0B14] border border-white/10 text-white text-sm rounded-lg h-9 px-3"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value as any)}
                  aria-label="Filter by type"
                >
                  <option>All</option>
                  <option>Project</option>
                  <option>Individual</option>
                </select>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 text-[#888888] hover:text-white hover:bg-white/5 rounded-lg" title="Sort options">
                <span className="material-symbols-outlined text-2xl">sort</span>
              </button>
              <button className="p-2 text-[#888888] hover:text-white hover:bg-white/5 rounded-lg" title="Help on filtering">
                <span className="material-symbols-outlined text-2xl">help</span>
              </button>
            </div>
          </div>

          {/* Scans Table */}
          <div className="bg-[#131523] rounded-lg border border-[#2E2E3F]/50 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-[#E0E0E0]" role="grid">
                <thead className="text-xs text-[#9da1b8] uppercase bg-[#0A0B14]">
                  <tr>
                    <th scope="col" className="px-6 py-4">Severity</th>
                    <th scope="col" className="px-6 py-4">Scan Target</th>
                    <th scope="col" className="px-6 py-4">Project</th>
                    <th scope="col" className="px-6 py-4">Type</th>
                    <th scope="col" className="px-6 py-4">Status</th>
                    <th scope="col" className="px-6 py-4">Date</th>
                  </tr>
                </thead>
                <tbody aria-live="polite">
                  {loading ? (
                    [...Array(6)].map((_, i) => (
                      <tr key={i} className="border-t border-[#2E2E3F]/50 animate-pulse">
                        <td className="px-6 py-4"><div className="w-3 h-3 rounded-full bg-[#1E2A3A]" /></td>
                        <td className="px-6 py-4"><div className="h-4 w-40 bg-[#1E2A3A] rounded" /></td>
                        <td className="px-6 py-4"><div className="h-4 w-32 bg-[#1E2A3A] rounded" /></td>
                        <td className="px-6 py-4"><div className="h-4 w-24 bg-[#1E2A3A] rounded" /></td>
                        <td className="px-6 py-4"><div className="h-4 w-24 bg-[#1E2A3A] rounded" /></td>
                        <td className="px-6 py-4"><div className="h-4 w-28 bg-[#1E2A3A] rounded" /></td>
                      </tr>
                    ))
                  ) : (
                    filteredScans.map((scan) => {
                      const project = scan.projectId
                        ? mockProjects.find((p) => p.id === scan.projectId)
                        : undefined;
                      const type = scan.projectId ? 'Project' : 'Individual';
                      const severityDot = scan.severity.critical
                        ? '#FF3B30'
                        : scan.severity.high
                        ? '#FF9500'
                        : scan.severity.medium
                        ? '#FFCC00'
                        : '#007AFF';
                      return (
                        <tr
                          key={scan.id}
                          className="border-t border-[#2E2E3F]/50 hover:bg-[#1A1B23]/50 cursor-pointer focus:bg-[#1A1B23]/60 focus:outline-none"
                          tabIndex={0}
                          onClick={() => onRowActivate(scan)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') onRowActivate(scan);
                          }}
                          title={
                            scan.severity.critical
                              ? 'Critical issues present'
                              : scan.severity.high
                              ? 'High severity issues present'
                              : scan.severity.medium
                              ? 'Medium severity issues present'
                              : 'Low severity issues present'
                          }
                        >
                          <td className="px-6 py-4">
                            <div
                              className="w-2.5 h-2.5 rounded-full"
                              style={{ backgroundColor: severityDot }}
                            />
                          </td>
                          <td className="px-6 py-4 font-medium text-white whitespace-nowrap">{scan.target}</td>
                          <td className="px-6 py-4 text-[#9da1b8]">{project?.name || '-'}</td>
                          <td className="px-6 py-4">
                            <span className="text-xs px-2 py-0.5 rounded-full border border-white/10 bg-white/5">
                              {type}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-xs px-2 py-0.5 rounded-full border border-white/10 bg-white/5">
                              {scan.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-[#9da1b8]">{scan.date}</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ReportsLandingPage;