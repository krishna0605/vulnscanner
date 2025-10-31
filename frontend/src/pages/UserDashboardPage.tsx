import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

const UserDashboardPage: React.FC = () => {
  const [profileOpen, setProfileOpen] = React.useState(false);
  const navigate = useNavigate();
  const profileRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const onDocMouseDown = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocMouseDown);
    return () => document.removeEventListener('mousedown', onDocMouseDown);
  }, []);
  return (
    <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full">
      {/* Background grid and aurora accents */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-transparent bg-[radial-gradient(#1A1A2E_1px,transparent_1px)] [background-size:32px_32px]" />
      <div className="absolute top-0 left-0 -z-10 h-1/2 w-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(74,144,226,0.3),rgba(255,255,255,0))]" />

      <div className="relative flex min-h-screen w-full overflow-hidden">
        {/* Sidebar hidden to match reference navbar-only layout */}
        <aside className="hidden">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3 px-2 py-4">
              <div
                className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10"
                style={{
                  backgroundImage:
                    'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAoGb6izEyw_X-IY8P4G1a15e7o30ltLXJVnqKuWW_bw3qlnzlNNTYrEnkZXhnNLOZHJAuVURDsIy0yKJ7KWbV5ulHg8NFsUL2QIoXSgs3tLTs46S3zXpP3WpI1co60H8nXr7VC9fJbj0cdMT5dL9n4F2bRQo20AdUqCu9h7m8G7YlLEnUZVXjv39K5ticnvVqwC6wCVyIQxyYAJcZ9UhO93dRoTmg_8WKC7IOoAhK-PraBlN-2I9Qr5IK5rlI__qB-QTLv_Fmr4eNx")',
                }}
              />
              <div className="flex flex-col">
                <h1 className="text-[#E0E0E0] text-base font-bold leading-normal">VulnScanner</h1>
                {/* Removed tagline per request */}
              </div>
            </div>
            <nav className="flex flex-col gap-2">
              <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-[#4A90E2]/20 text-[#4A90E2]">
                <span className="material-symbols-outlined fill">dashboard</span>
                <p className="text-sm font-medium leading-normal">Dashboard</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-[#E0E0E0] hover:bg-white/10 rounded-lg transition-colors">
                <span className="material-symbols-outlined">folder</span>
                <p className="text-sm font-medium leading-normal">Projects</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-[#E0E0E0] hover:bg-white/10 rounded-lg transition-colors">
                <span className="material-symbols-outlined">radar</span>
                <p className="text-sm font-medium leading-normal">Scans</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-[#E0E0E0] hover:bg-white/10 rounded-lg transition-colors">
                <span className="material-symbols-outlined">bar_chart</span>
                <p className="text-sm font-medium leading-normal">Reports</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-[#E0E0E0] hover:bg-white/10 rounded-lg transition-colors">
                <span className="material-symbols-outlined">settings</span>
                <p className="text-sm font-medium leading-normal">Settings</p>
              </div>
            </nav>
          </div>
        </aside>

        {/* Main area */}
        <main className="flex-1 flex flex-col overflow-y-auto">
          {/* Top navbar (aligned with reference layout) */}
          <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div
                  className="flex items-center gap-3 cursor-pointer"
                  onClick={() => navigate('/dashboard')}
                >
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
                  <Link to="/dashboard" className="nav-link active relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-white transition-all duration-300"><span className="material-symbols-outlined fill text-base">dashboard</span>Dashboard</Link>
                  <Link to="/projects" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all duration-300"><span className="material-symbols-outlined text-base">folder</span>Projects</Link>
                  <Link to="/scans" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all duration-300"><span className="material-symbols-outlined text-base">radar</span>Scans</Link>
                  <Link to="/reports" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all duration-300"><span className="material-symbols-outlined text-base">bar_chart</span>Reports</Link>
                  <Link to="/settings" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all duration-300"><span className="material-symbols-outlined text-base">settings</span>Settings</Link>
                </nav>
              </div>
              <div className="flex flex-1 items-center justify-end gap-2 sm:gap-4">
                <label className="hidden sm:flex flex-col min-w-40 h-10 max-w-sm">
                  <div className="flex w-full items-stretch rounded-lg h-full">
                    <div className="text-[#888888] flex bg-[#131523]/80 items-center justify-center pl-4 rounded-l-lg">
                      <span className="material-symbols-outlined">search</span>
                    </div>
                    <input
                      className="form-input flex w-full flex-1 rounded-lg text-[#E0E0E0] focus:outline-0 focus:ring-2 focus:ring-[#4A90E2] border-none bg-[#131523]/80 h-full placeholder:text-[#888888] px-4 rounded-l-none pl-2 text-sm"
                      placeholder="Search projects..."
                    />
                  </div>
                </label>
                <button className="relative flex cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 w-10 bg-[#131523]/80 text-[#E0E0E0] hover:text-[#4A90E2] transition-colors">
                  <span className="material-symbols-outlined">notifications</span>
                  <div className="absolute top-1.5 right-1.5 size-2.5 rounded-full bg-[#FF4C4C] border-2 border-[#131523]" />
                </button>
                <div
                  ref={profileRef}
                  className="relative flex items-center gap-3 cursor-pointer"
                  onClick={() => setProfileOpen((prev) => !prev)}
                >
                  <div
                    className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10"
                    style={{
                      backgroundImage:
                        'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCdOaINXzXPCl8Y-hFtI2ZnqmHTZKt2zgKT9uHSGm-z3XPbz2KkoxPACXtQpwqHMzoUnl9T4S74vWsmm4LS9qRskXRkAUylHMCkSvQWSQ9YfsHQ8R6H63cd688VgoEbPDvaosSdfujXd-sU7UXHqutC_Hs7Nj7E__VwTfRG7VliMn9e4zxPdndtPe_olK3eRVzUvpUQxPgE8Fvcv3IOoXWlvZAz_s_G3MlS9elim3BLzT-xI7wx_tZbYQT6hmkCvAi1ic918YIy--0Q")',
                    }}
                  />
                  <div className="text-right hidden sm:block">
                    <p className="text-[#E0E0E0] text-sm font-medium">Alex Drake</p>
                    <p className="text-[#888888] text-xs">Admin</p>
                  </div>
                  {/* Profile dropdown (click to toggle; stays open while interacting) */}
                  <div
                    className={`absolute right-0 top-full mt-2 w-44 rounded-lg border border-[#2E2E3F]/60 bg-[#131523]/95 backdrop-blur-sm shadow-2xl shadow-black/50 p-1 ${profileOpen ? 'block' : 'hidden'}`}
                    role="menu"
                    aria-label="Profile menu"
                  >
                    <button
                      className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[#E0E0E0] hover:bg-[#2E2E3F] rounded"
                      role="menuitem"
                      onClick={() => { setProfileOpen(false); navigate('/profile'); }}
                    >
                      <span className="material-symbols-outlined text-base">person</span>
                      Profile
                    </button>
                    <button
                      className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[#E0E0E0] hover:bg-[#2E2E3F] rounded"
                      role="menuitem"
                      onClick={() => setProfileOpen(false)}
                    >
                      <span className="material-symbols-outlined text-base">settings</span>
                      Settings
                    </button>
                    <button
                      className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[#FF4C4C] hover:bg-[#2E2E3F] rounded"
                      role="menuitem"
                      onClick={() => setProfileOpen(false)}
                    >
                      <span className="material-symbols-outlined text-base">logout</span>
                      Logout
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Content */}
          <div className="flex-1 p-6 md:p-8 lg:p-10 space-y-8">
            {/* Title and actions */}
            <div className="flex flex-wrap justify-between items-start gap-4">
              <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold leading-tight">Dashboard</h1>
                <p className="text-[#888888] text-base">Welcome back. Here's a summary of your security posture.</p>
              </div>
              <div className="flex flex-1 sm:flex-initial gap-3 flex-wrap justify-start sm:justify-end">
                <button onClick={() => navigate('/scans/new')} className="relative group flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#4A90E2] text-white text-sm font-bold gap-2 transition-all duration-300 hover:shadow-[0_0_20px_0px_#4a90e280]">
                  <span className="material-symbols-outlined transition-transform duration-300 group-hover:rotate-90">add</span>
                  <span className="truncate">New Scan</span>
                </button>
                <button onClick={() => navigate('/projects/new')} className="flex min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#131523] text-[#E0E0E0] text-sm font-bold border border-[#2E2E3F] hover:bg-[#2E2E3F] hover:text-white transition-colors">
                  <span className="truncate">New Project</span>
                </button>
                {/* Removed redundant View Reports button (available in top navbar) */}
              </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="flex flex-col gap-2 rounded-xl p-6 bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm">
                <p className="text-[#888888] text-sm font-medium">Total Projects</p>
                <p className="tracking-tight text-4xl font-bold">24</p>
              </div>
              <div className="flex flex-col gap-2 rounded-xl p-6 bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm">
                <p className="text-[#888888] text-sm font-medium">Active Scans</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-[#4A90E2] tracking-tight text-4xl font-bold">3</p>
                  <div className="w-16 h-2 bg-[#4A90E2]/20 rounded-full overflow-hidden">
                    <div className="w-3/4 h-full bg-[#4A90E2] animate-pulse" />
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-2 rounded-xl p-6 bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm">
                <p className="text-[#888888] text-sm font-medium">Vulnerabilities Found</p>
                <p className="text-[#FF4C4C] tracking-tight text-4xl font-bold">157</p>
              </div>
            </div>

            {/* Projects and Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Projects list */}
              <div className="lg:col-span-2 space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold">My Projects</h2>
                  <div className="flex items-center gap-1">
                    <button className="text-[#888888] p-2 rounded-md hover:bg-[#131523]"><span className="material-symbols-outlined">grid_view</span></button>
                    <button className="text-[#4A90E2] bg-[#4A90E2]/20 p-2 rounded-md"><span className="material-symbols-outlined">list</span></button>
                  </div>
                </div>
                <div className="flex flex-col gap-4">
                  {/* Card 1 */}
                  <div onClick={() => navigate('/projects/1')} className="group flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm hover:border-[#4A90E2] transition-all cursor-pointer">
                    <div className="flex-1">
                      <p className="font-semibold">E-commerce Platform</p>
                      <p className="text-[#888888] text-sm">webapp.example.com</p>
                    </div>
                    <div className="flex-1 flex flex-col sm:items-center">
                      <p className="text-[#888888] text-sm">Last Scan</p>
                      <p className="font-medium">2 hours ago</p>
                    </div>
                    <div className="flex-1 flex flex-col sm:items-center">
                      <p className="text-[#888888] text-sm">Vulnerabilities</p>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-[#FF4C4C]"></span><span className="text-[#FF4C4C] font-bold text-sm">5</span></div>
                        <div className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-[#FFB833]"></span><span className="text-[#FFB833] font-bold text-sm">12</span></div>
                        <div className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-[#888888]"></span><span className="text-[#888888] font-bold text-sm">34</span></div>
                      </div>
                    </div>
                    <div className="flex-1 flex sm:justify-end">
                      <span className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full bg-[#00C853]/10 text-[#00C853] ring-1 ring-inset ring-[#00C853]/30">
                        <span className="size-2 rounded-full bg-[#00C853] futuristic-glow-success"></span> Completed
                      </span>
                    </div>
                  </div>

                  {/* Card 2 */}
                  <div onClick={() => navigate('/projects/2')} className="group flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm hover:border-[#4A90E2] transition-all cursor-pointer">
                    <div className="flex-1">
                      <p className="font-semibold">Marketing Site</p>
                      <p className="text-[#888888] text-sm">corporate-site.io</p>
                    </div>
                    <div className="flex-1 flex flex-col sm:items-center">
                      <p className="text-[#888888] text-sm">Last Scan</p>
                      <p className="font-medium">1 day ago</p>
                    </div>
                    <div className="flex-1 flex flex-col sm:items-center">
                      <p className="text-[#888888] text-sm">Vulnerabilities</p>
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-[#FF4C4C]"></span><span className="text-[#FF4C4C] font-bold text-sm">1</span></div>
                        <div className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-[#FFB833]"></span><span className="text-[#FFB833] font-bold text-sm">3</span></div>
                        <div className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-[#888888]"></span><span className="text-[#888888] font-bold text-sm">8</span></div>
                      </div>
                    </div>
                    <div className="flex-1 flex sm:justify-end">
                      <span className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full bg-[#00C853]/10 text-[#00C853] ring-1 ring-inset ring-[#00C853]/30">
                        <span className="size-2 rounded-full bg-[#00C853] futuristic-glow-success"></span> Completed
                      </span>
                    </div>
                  </div>

                  {/* Card 3 */}
                  <div onClick={() => navigate('/projects/3')} className="group flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-lg bg-[#131523]/80 border border-[#2E2E3F]/60 backdrop-blur-sm hover:border-[#4A90E2] transition-all cursor-pointer">
                    <div className="flex-1">
                      <p className="font-semibold">API Gateway</p>
                      <p className="text-[#888888] text-sm">api.service.net</p>
                    </div>
                    <div className="flex-1 flex flex-col sm:items-center">
                      <p className="text-[#888888] text-sm">Last Scan</p>
                      <p className="font-medium">In Progress</p>
                    </div>
                    <div className="flex-1 flex flex-col sm:items-center">
                      <p className="text-[#888888] text-sm">Vulnerabilities</p>
                      <div className="flex items-center gap-2">
                        <span className="text-[#888888] font-bold">--</span>
                      </div>
                    </div>
                    <div className="flex-1 flex sm:justify-end">
                      <span className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full bg-[#4A90E2]/10 text-[#4A90E2] ring-1 ring-inset ring-[#4A90E2]/30">
                        <span className="size-2 rounded-full bg-[#4A90E2] futuristic-glow-primary animate-pulse"></span> Scanning
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="space-y-6">
                <h2 className="text-xl font-bold">Recent Activity</h2>
                <ul className="relative space-y-6 activity-timeline">
                  <li className="flex items-start gap-4 activity-item">
                    <div className="activity-dot flex-shrink-0 mt-1 flex items-center justify-center size-9 rounded-full bg-[#131523] border border-[#00C853]/50 relative"><span className="size-2 rounded-full bg-[#00C853] animate-pulseGlow"></span></div>
                    <div>
                      <p className="text-sm font-medium">Scan on <span className="font-bold text-[#4A90E2]/90">E-commerce Platform</span> completed.</p>
                      <p className="text-[#888888] text-xs">2 hours ago</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-4 activity-item">
                    <div className="activity-dot flex-shrink-0 mt-1 flex items-center justify-center size-9 rounded-full bg-[#131523] border border-[#FFB833]/50 relative"><span className="size-2 rounded-full bg-[#FFB833]"></span></div>
                    <div>
                      <p className="text-sm font-medium">New <span className="font-bold text-[#FFB833]">High</span> vulnerability found in <span className="font-bold text-[#4A90E2]/90">Marketing Site</span>.</p>
                      <p className="text-[#888888] text-xs">1 day ago</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-4 activity-item">
                    <div className="activity-dot flex-shrink-0 mt-1 flex items-center justify-center size-9 rounded-full bg-[#131523] border border-[#4A90E2]/50 relative"><span className="size-2 rounded-full bg-[#4A90E2]"></span></div>
                    <div>
                      <p className="text-sm font-medium">New project <span className="font-bold text-[#4A90E2]/90">"Client Portal"</span> was created.</p>
                      <p className="text-[#888888] text-xs">2 days ago</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-4 activity-item">
                    <div className="activity-dot flex-shrink-0 mt-1 flex items-center justify-center size-9 rounded-full bg-[#131523] border border-[#FF4C4C]/50 relative"><span className="size-2 rounded-full bg-[#FF4C4C]"></span></div>
                    <div>
                      <p className="text-sm font-medium">New <span className="font-bold text-[#FF4C4C]">Critical</span> vulnerability found in <span className="font-bold text-[#4A90E2]/90">E-commerce Platform</span>.</p>
                      <p className="text-[#888888] text-xs">2 days ago</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default UserDashboardPage;