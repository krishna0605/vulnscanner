import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

const ProjectDetailsPage: React.FC = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();

  // Mock project data; in a real app, fetch by projectId
  const project = {
    id: projectId || 'omega',
    name: projectId === '1' ? 'E-commerce Platform' : projectId === '2' ? 'Corporate Website' : projectId === '3' ? 'Marketing Landing Page' : 'Project Omega',
    url: projectId === '1' ? 'https://example-shop.com' : projectId === '2' ? 'https://ourbusiness.com' : projectId === '3' ? 'https://promo.example.com' : 'https://example.com',
    schedule: 'Daily at 3:00 AM UTC',
    notifications: 'Enabled for Critical & High',
    summary: { critical: 12, high: 35, medium: 89, low: 152, total: 288 },
  };

  return (
    <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full">
      {/* Background accents */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-transparent bg-[radial-gradient(#1A1A2E_1px,transparent_1px)] [background-size:50px_50px] animate-[grid-pan_60s_linear_infinite]" />
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-transparent to-[#0A0B14]" />

      {/* Top navbar */}
      <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
        <div className="flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-3 cursor-pointer">
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
          </Link>
          <nav className="hidden md:flex items-center gap-4">
            <Link to="/projects" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all"><span className="material-symbols-outlined text-base">folder</span>Projects</Link>
            <Link to="/profile" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all"><span className="material-symbols-outlined text-base">settings</span>Settings</Link>
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="flex w-full max-w-7xl mx-auto flex-1 flex-col px-4 sm:px-6 md:px-8 py-6">
        {/* Breadcrumbs and heading */}
        <div className="flex items-center gap-2 text-sm text-[#888888] mb-6 px-1">
          <Link to="/projects" className="hover:text-[#4A90E2] transition-colors">Projects</Link>
          <span className="material-symbols-outlined !text-base">chevron_right</span>
          <span className="text-white">{project.name}</span>
        </div>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 flex items-center justify-center bg-[#131523] border border-[#2E2E3F] rounded-lg">
              <span className="material-symbols-outlined text-[#4A90E2] !text-3xl">shield</span>
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold leading-tight text-white">{project.name}</h1>
              <p className="text-sm text-[#888888]">{project.url}</p>
            </div>
          </div>
          <div className="flex flex-shrink-0 gap-3">
            <button className="flex min-w-[84px] items-center justify-center gap-2 rounded-lg h-10 px-5 bg-[#4A90E2] text-black text-sm font-bold transition-all hover:bg-white hover:shadow-[0_0_20px_0px_#4a90e280]" onClick={() => navigate('/scans/new')}>
              <span className="material-symbols-outlined text-base">rocket_launch</span>
              <span>New Scan</span>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="sticky top-14 z-20 bg-[#0A0B14]/80 backdrop-blur-sm">
          <div className="relative border-b border-[#2E2E3F] flex gap-6 md:gap-8 px-1">
            <button className="relative px-2 py-4 text-sm font-semibold text-[#4A90E2]">Settings</button>
            <button className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">Scans</button>
            <button className="relative px-2 py-4 text-sm font-semibold text-[#888888] hover:text-white transition-colors">Findings</button>
            <div className="absolute bottom-0 left-2 h-0.5 w-16 bg-[#4A90E2] shadow-[0_0_10px_#4A90E2]" />
          </div>
        </div>

        {/* Project Configuration */}
        <section className="mt-8">
          <h2 className="text-lg font-semibold text-white mb-4">Project Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-[#131523]/80 border border-[#2E2E3F] rounded-lg p-5 flex items-start gap-4 hover:border-[#4A90E2]/50 transition-colors">
              <span className="material-symbols-outlined text-[#4A90E2] mt-1">link</span>
              <div>
                <h3 className="font-semibold text-white">Target URL</h3>
                <p className="text-sm text-[#888888]">{project.url}</p>
              </div>
            </div>
            <div className="bg-[#131523]/80 border border-[#2E2E3F] rounded-lg p-5 flex items-start gap-4 hover:border-[#4A90E2]/50 transition-colors">
              <span className="material-symbols-outlined text-[#4A90E2] mt-1">schedule</span>
              <div>
                <h3 className="font-semibold text-white">Scan Schedule</h3>
                <p className="text-sm text-[#888888]">{project.schedule}</p>
              </div>
            </div>
            <div className="bg-[#131523]/80 border border-[#2E2E3F] rounded-lg p-5 flex items-start gap-4 hover:border-[#4A90E2]/50 transition-colors">
              <span className="material-symbols-outlined text-[#4A90E2] mt-1">notifications</span>
              <div>
                <h3 className="font-semibold text-white">Notifications</h3>
                <p className="text-sm text-[#888888]">{project.notifications}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Vulnerability Summary */}
        <section className="mt-8">
          <h2 className="text-lg font-semibold text-white mb-4">Vulnerability Summary</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-[#131523]/80 border border-[#FF4C4C]/40 rounded-lg p-5 hover:border-[#FF4C4C] transition-colors">
              <p className="text-sm font-medium text-[#FF4C4C]">Critical</p>
              <p className="text-3xl font-bold text-white">{project.summary.critical}</p>
            </div>
            <div className="bg-[#131523]/80 border border-[#FFB833]/40 rounded-lg p-5 hover:border-[#FFB833] transition-colors">
              <p className="text-sm font-medium text-[#FFB833]">High</p>
              <p className="text-3xl font-bold text-white">{project.summary.high}</p>
            </div>
            <div className="bg-[#131523]/80 border border-[#FFD700]/40 rounded-lg p-5 hover:border-[#FFD700] transition-colors">
              <p className="text-sm font-medium text-[#FFD700]">Medium</p>
              <p className="text-3xl font-bold text-white">{project.summary.medium}</p>
            </div>
            <div className="bg-[#131523]/80 border border-[#00F0FF]/40 rounded-lg p-5 hover:border-[#00F0FF] transition-colors">
              <p className="text-sm font-medium text-[#00F0FF]">Low</p>
              <p className="text-3xl font-bold text-white">{project.summary.low}</p>
            </div>
          </div>
        </section>

        {/* Recent Activity & Severity Distribution */}
        <section className="mt-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-[#131523]/80 border border-[#2E2E3F] rounded-lg p-6 flex flex-col items-center justify-center">
              <h3 className="text-base font-semibold text-white mb-4 self-start">Severity Distribution</h3>
              <div className="relative w-44 h-44">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="12" />
                  <circle cx="60" cy="60" r="54" fill="none" stroke="#FF4C4C" strokeDasharray="12.02, 339.29" strokeLinecap="round" strokeWidth="12" />
                  <circle cx="60" cy="60" r="54" fill="none" stroke="#FFB833" strokeDasharray="39.67, 339.29" strokeDashoffset="-12.02" strokeLinecap="round" strokeWidth="12" />
                  <circle cx="60" cy="60" r="54" fill="none" stroke="#FFD700" strokeDasharray="97.23, 339.29" strokeDashoffset="-51.69" strokeLinecap="round" strokeWidth="12" />
                  <circle cx="60" cy="60" r="54" fill="none" stroke="#00F0FF" strokeDasharray="190.38, 339.29" strokeDashoffset="-148.92" strokeLinecap="round" strokeWidth="12" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-white">{project.summary.total}</span>
                  <span className="text-sm text-[#888888]">Total</span>
                </div>
              </div>
            </div>
            <div className="lg:col-span-2 bg-[#131523]/80 border border-[#2E2E3F] rounded-lg p-6">
              <h3 className="text-base font-semibold text-white mb-4">Recent Activity</h3>
              <div className="flow-root">
                <ul className="-mb-6">
                  <li className="relative pb-6">
                    <div className="absolute left-3 top-3 -ml-px h-full w-0.5 bg-[#2E2E3F]" />
                    <div className="relative flex items-center gap-4">
                      <span className="relative flex h-6 w-6 items-center justify-center rounded-full bg-green-500/20 ring-4 ring-[#131523]">
                        <span className="material-symbols-outlined text-sm text-green-400">task_alt</span>
                      </span>
                      <div className="flex-auto"><p className="text-sm text-[#888888]">Scan #42 completed. <span className="text-white">3 new findings.</span></p></div>
                      <time className="flex-none py-0.5 text-xs leading-5 text-[#888888]">3h ago</time>
                    </div>
                  </li>
                  <li className="relative pb-6">
                    <div className="absolute left-3 top-3 -ml-px h-full w-0.5 bg-[#2E2E3F]" />
                    <div className="relative flex items-center gap-4">
                      <span className="relative flex h-6 w-6 items-center justify-center rounded-full bg-blue-500/20 ring-4 ring-[#131523]">
                        <span className="material-symbols-outlined text-sm text-blue-400">play_arrow</span>
                      </span>
                      <div className="flex-auto"><p className="text-sm text-[#888888]">Scan initiated by <span className="text-white">Alex Morgan</span></p></div>
                      <time className="flex-none py-0.5 text-xs leading-5 text-[#888888]">4h ago</time>
                    </div>
                  </li>
                  <li className="relative pb-6">
                    <div className="absolute left-3 top-3 -ml-px h-full w-0.5 bg-[#2E2E3F]" />
                    <div className="relative flex items-center gap-4">
                      <span className="relative flex h-6 w-6 items-center justify-center rounded-full bg-yellow-500/20 ring-4 ring-[#131523]">
                        <span className="material-symbols-outlined text-sm text-yellow-400">notification_important</span>
                      </span>
                      <div className="flex-auto"><p className="text-sm text-[#888888]">New High finding: <span className="text-white">SQL Injection</span></p></div>
                      <time className="flex-none py-0.5 text-xs leading-5 text-[#888888]">1d ago</time>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default ProjectDetailsPage;