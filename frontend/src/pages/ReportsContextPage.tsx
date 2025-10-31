import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

type SeveritySummary = { critical: number; high: number; medium: number; low: number };
type Project = { id: number; name: string; owner?: string };
type Scan = {
  id: number;
  target: string;
  date: string;
  status: 'Completed' | 'Warnings' | 'Critical Found' | 'Cancelled' | 'Running';
  severity: SeveritySummary;
  projectId: number | null;
};
type Finding = {
  id: number;
  title: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  cve?: string;
};

const projects: Project[] = [
  { id: 1, name: 'Project Phoenix', owner: 'CyberCorp' },
  { id: 2, name: 'E-Commerce Platform', owner: 'ShopCo' },
];
const scans: Scan[] = [
  { id: 101, target: 'example.com', date: '2023-10-26 14:30', status: 'Completed', severity: { critical: 5, high: 15, medium: 22, low: 8 }, projectId: 1 },
  { id: 102, target: 'secure-api.dev', date: '2023-10-25 09:15', status: 'Critical Found', severity: { critical: 5, high: 12, medium: 18, low: 4 }, projectId: null },
  { id: 103, target: 'e-commerce-store.com', date: '2023-10-24 22:00', status: 'Warnings', severity: { critical: 0, high: 8, medium: 22, low: 11 }, projectId: 2 },
];
const findingsByScan: Record<number, Finding[]> = {
  101: [
    { id: 500, title: 'Insecure Deserialization', severity: 'Critical', cve: 'CVE-2023-12345' },
    { id: 501, title: 'SQL Injection', severity: 'High', cve: 'CVE-2023-54321' },
    { id: 502, title: 'Cross-Site Scripting (XSS)', severity: 'Medium', cve: 'CVE-2023-24680' },
  ],
  102: [
    { id: 600, title: 'Broken Access Control', severity: 'High' },
    { id: 601, title: 'CSRF', severity: 'Low' },
  ],
  103: [
    { id: 700, title: 'Insecure Deserialization', severity: 'Critical' },
  ],
};

const ReportsContextPage: React.FC = () => {
  const navigate = useNavigate();
  const params = useParams();
  const projectId = params.projectId ? Number(params.projectId) : undefined;
  const scanId = params.scanId ? Number(params.scanId) : undefined;
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState<'All' | 'Critical' | 'High' | 'Medium' | 'Low'>('All');

  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 400);
    return () => clearTimeout(t);
  }, []);

  const contextProject = projectId ? projects.find((p) => p.id === projectId) : undefined;
  const contextScan = scanId ? scans.find((s) => s.id === scanId) : undefined;

  const scansForProject = useMemo(() => {
    if (!contextProject) return [];
    return scans.filter((s) => s.projectId === contextProject.id);
  }, [contextProject]);

  const findings = useMemo(() => {
    const data = contextScan ? findingsByScan[contextScan.id] || [] : [];
    return data.filter((f) => severityFilter === 'All' || f.severity === severityFilter);
  }, [contextScan, severityFilter]);

  const headerTitle = contextProject
    ? `Project Report: ${contextProject.name}`
    : contextScan
    ? `Scan Report: ${contextScan.target}`
    : 'Report';

  const onFindingClick = (finding: Finding) => {
    if (contextScan) {
      navigate(`/reports/scan/${contextScan.id}/findings/${finding.id}`);
    }
  };

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
              <span className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#00FFFF]"><span className="material-symbols-outlined text-base">bar_chart</span>Reports</span>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <button className="group relative inline-flex items-center justify-center gap-2 rounded-lg bg-[#00BFFF]/20 px-4 py-2 text-sm font-medium text-[#00BFFF] transition-all hover:bg-[#00BFFF]/30" title="Export as PDF">
              <span className="material-symbols-outlined">picture_as_pdf</span>
              Export PDF
            </button>
            <button className="group relative inline-flex items-center justify-center gap-2 rounded-lg bg-[#00BFFF]/20 px-4 py-2 text-sm font-medium text-[#00BFFF] transition-all hover:bg-[#00BFFF]/30" title="Export as CSV">
              <span className="material-symbols-outlined">csv</span>
              Export CSV
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="px-4 sm:px-10 flex flex-1 justify-center py-8">
        <div className="max-w-7xl w-full flex flex-col gap-8">
          {/* Breadcrumbs */}
          <div className="flex flex-wrap gap-2" aria-label="Breadcrumb">
            <Link to="/dashboard" className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Dashboard</Link>
            <span className="text-[#9da1b8] text-sm">/</span>
            <Link to="/reports" className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Reports</Link>
            {contextProject && (
              <>
                <span className="text-[#9da1b8] text-sm">/</span>
                <span className="text-white text-sm">{contextProject.name}</span>
              </>
            )}
            {contextScan && (
              <>
                <span className="text-[#9da1b8] text-sm">/</span>
                <span className="text-white text-sm">Scan #{contextScan.id}</span>
              </>
            )}
          </div>

          {/* Header */}
          <div className="flex flex-wrap justify-between items-start gap-4">
            <div className="flex flex-col gap-1">
              <p className="text-white text-3xl sm:text-4xl font-black leading-tight">{headerTitle}</p>
              {contextScan && (
                <p className="text-white/60 text-base">Scan completed on {contextScan.date}</p>
              )}
            </div>
            {contextProject && (
              <div className="flex items-center gap-3 text-sm">
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 bg-white/5 border border-white/10">Owner: {contextProject.owner}</span>
              </div>
            )}
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="flex flex-col gap-2 rounded-xl p-6 bg-[#1A1B23] border border-white/10">
              <p className="text-white/80 text-base">Total Vulnerabilities</p>
              <p className="text-white text-3xl font-bold">{contextScan ? (contextScan.severity.critical + contextScan.severity.high + contextScan.severity.medium + contextScan.severity.low) : scansForProject.reduce((acc, s) => acc + s.severity.critical + s.severity.high + s.severity.medium + s.severity.low, 0)}</p>
            </div>
            <div className="flex flex-col gap-2 rounded-xl p-6 bg-[#1A1B23] border border-white/10">
              <p className="text-white/80 text-base">High Severity</p>
              <p className="text-[#FFA500] text-3xl font-bold">{contextScan ? contextScan.severity.high : scansForProject.reduce((acc, s) => acc + s.severity.high, 0)}</p>
            </div>
            <div className="flex flex-col gap-2 rounded-xl p-6 bg-[#1A1B23] border border-white/10">
              <p className="text-white/80 text-base">Critical</p>
              <p className="text-[#FF455F] text-3xl font-bold">{contextScan ? contextScan.severity.critical : scansForProject.reduce((acc, s) => acc + s.severity.critical, 0)}</p>
            </div>
          </div>

          {/* Project Scans List */}
          {contextProject && (
            <section className="flex flex-col gap-4">
              <h3 className="text-white text-lg font-bold">Scans in {contextProject.name}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {scansForProject.map((s) => (
                  <button key={s.id} className="text-left rounded-xl p-4 bg-[#1A1B23] border border-white/10 hover:bg-white/5 transition-colors" onClick={() => navigate(`/reports/scan/${s.id}`)} aria-label={`Open scan ${s.id}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-bold">{s.target}</p>
                        <p className="text-white/60 text-sm">{s.date}</p>
                      </div>
                      <span className="text-xs px-2 py-0.5 rounded-full border border-white/10 bg-white/5">{s.status}</span>
                    </div>
                    <div className="mt-3 text-sm text-white/70">Critical: {s.severity.critical}, High: {s.severity.high}, Medium: {s.severity.medium}, Low: {s.severity.low}</div>
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* Top vulnerability types */}
          <section className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <div className="lg:col-span-2 flex flex-col gap-4 rounded-xl p-6 bg-[#1A1B23] border border-white/10">
              <h3 className="text-white text-lg font-bold">Vulnerabilities by Severity</h3>
              <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <div className="flex items-center gap-2"><span className="size-3 rounded-full" style={{ backgroundColor: '#FF455F' }}></span><span>Critical</span></div>
                <div className="flex items-center gap-2"><span className="size-3 rounded-full" style={{ backgroundColor: '#FFA500' }}></span><span>High</span></div>
                <div className="flex items-center gap-2"><span className="size-3 rounded-full" style={{ backgroundColor: '#FFD700' }}></span><span>Medium</span></div>
                <div className="flex items-center gap-2"><span className="size-3 rounded-full" style={{ backgroundColor: '#00B8A9' }}></span><span>Low</span></div>
              </div>
            </div>
            <div className="lg:col-span-3 flex flex-col gap-4 rounded-xl p-6 bg-[#1A1B23] border border-white/10">
              <h3 className="text-white text-lg font-bold">Top 5 Vulnerability Types</h3>
              <div className="flex flex-col gap-4">
                {['SQL Injection', 'Cross-Site Scripting (XSS)', 'Insecure Deserialization', 'Broken Access Control', 'CSRF'].map((name, idx) => (
                  <div key={idx} className="flex flex-col gap-1.5">
                    <p className="text-sm text-white/80">{name}</p>
                    <div className="w-full bg-white/10 rounded-full h-2.5"><div className="bg-[#FFA500] h-2.5 rounded-full" style={{ width: `${70 - idx * 10}%` }}></div></div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Findings list */}
          {contextScan && (
            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-white text-2xl font-bold">Detailed Findings</h2>
                <div className="flex items-center gap-2">
                  <label className="text-white text-sm">Severity</label>
                  <select className="bg-[#0A0B14] border border-white/10 text-white text-sm rounded-lg h-9 px-3" value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value as any)} aria-label="Filter findings by severity">
                    <option>All</option>
                    <option>Critical</option>
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>
                </div>
              </div>
              {(loading ? [...Array(3)] : findings).map((item, i) => (
                <div key={item ? item.id : i} className="rounded-xl bg-[#1A1B23] border border-white/10 p-6">
                  {loading ? (
                    <div className="animate-pulse h-5 w-52 bg-[#1E2A3A] rounded" />
                  ) : (
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-bold text-white">{item.title}</h3>
                        <div className="mt-1 flex items-center gap-4 text-sm text-white/70">
                          <span className="inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium"
                            style={{ backgroundColor: item.severity === 'Critical' ? 'rgba(255,69,95,0.2)' : item.severity === 'High' ? 'rgba(255,165,0,0.2)' : item.severity === 'Medium' ? 'rgba(255,215,0,0.2)' : 'rgba(0,184,169,0.2)', color: item.severity === 'Critical' ? '#FF455F' : item.severity === 'High' ? '#FFA500' : item.severity === 'Medium' ? '#FFD700' : '#00B8A9' }}
                            title={`Severity: ${item.severity}`}
                          >
                            <span className="size-1.5 rounded-full" style={{ backgroundColor: item.severity === 'Critical' ? '#FF455F' : item.severity === 'High' ? '#FFA500' : item.severity === 'Medium' ? '#FFD700' : '#00B8A9' }}></span>
                            {item.severity}
                          </span>
                          {item.cve && (
                            <div className="flex items-center gap-1.5">
                              <span className="material-symbols-outlined text-base">tag</span>
                              <span>{item.cve}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button className="inline-flex items-center rounded-lg px-3 py-1 text-xs font-medium bg-white/5 border border-white/10 hover:bg-white/10 transition-colors" onClick={() => onFindingClick(item)} aria-label="Open finding details">
                          View Details
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </section>
          )}
        </div>
      </main>
    </div>
  );
};

export default ReportsContextPage;