import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const ProjectListPage: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full">
      {/* Background accents */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-transparent bg-[radial-gradient(#1A1A2E_1px,transparent_1px)] [background-size:32px_32px]" />
      <div className="absolute top-0 left-0 -z-10 h-1/2 w-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(74,144,226,0.14),rgba(255,255,255,0))]" />

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
            <Link to="/dashboard" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all"><span className="material-symbols-outlined text-base">dashboard</span>Dashboard</Link>
            <Link to="/projects" className="nav-link active relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-white transition-all"><span className="material-symbols-outlined text-base">folder</span>Projects</Link>
            <Link to="/profile" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all"><span className="material-symbols-outlined text-base">settings</span>Settings</Link>
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="px-4 sm:px-10 flex flex-1 justify-center py-8">
        <div className="layout-content-container flex flex-col w-full max-w-7xl flex-1 gap-6">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <h1 className="text-white text-3xl sm:text-4xl font-black leading-tight tracking-[-0.02em]">Projects</h1>
            <button
              className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-5 bg-[#4A90E2] hover:bg-[#3b7bc2] text-[#0A0B14] text-sm font-bold gap-2 transition-all shadow-[0_0_15px_0_rgba(74,144,226,0.5)]"
              onClick={() => navigate('/projects/new')}
            >
              <span className="material-symbols-outlined text-lg">add_circle</span>
              <span className="truncate">New Project</span>
            </button>
          </div>

          {/* Search and filters */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-grow">
              <div className="relative w-full max-w-xs group">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#888888] group-focus-within:text-[#4A90E2] transition-colors">search</span>
                <input className="w-full bg-[#131523]/80 text-white rounded-lg border border-[#2E2E3F] focus:border-[#4A90E2]/50 focus:ring-[#4A90E2]/20 focus:ring-2 pl-10 h-10 text-sm transition-all" placeholder="Search projects..." type="text" />
              </div>
              <div className="relative">
                <button className="flex h-10 items-center justify-center gap-x-2 rounded-lg bg-[#131523]/80 border border-[#2E2E3F] hover:border-[#4A90E2]/50 hover:text-white px-4 transition-all">
                  <span className="material-symbols-outlined text-[#888888] text-base">public</span>
                  <p className="text-[#E0E0E0] text-sm font-medium leading-normal">Status: All</p>
                  <span className="material-symbols-outlined text-[#888888] text-base">expand_more</span>
                </button>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-[#888888]">Sort by:</span>
              <button className="flex h-10 items-center justify-center gap-x-2 rounded-lg bg-[#131523]/80 border border-[#2E2E3F] hover:border-[#4A90E2]/50 hover:text-white px-4 transition-all">
                <p className="text-[#E0E0E0] text-sm font-medium leading-normal">Last Scan</p>
                <span className="material-symbols-outlined text-[#888888] text-base">arrow_downward</span>
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-hidden rounded-xl border border-[#2E2E3F]/60 bg-[#131523]/80 backdrop-blur-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="border-b border-[#2E2E3F]/60">
                  <tr>
                    <th className="px-6 py-4 font-medium text-[#C8C8D6] uppercase tracking-wider">Project Name</th>
                    <th className="px-6 py-4 font-medium text-[#C8C8D6] uppercase tracking-wider">Target URL</th>
                    <th className="px-6 py-4 font-medium text-[#C8C8D6] uppercase tracking-wider">Last Scan</th>
                    <th className="px-6 py-4 font-medium text-[#C8C8D6] uppercase tracking-wider">Status</th>
                    <th className="px-6 py-4 font-medium text-[#C8C8D6] uppercase tracking-wider whitespace-nowrap">Vulnerabilities</th>
                    <th className="px-6 py-4 font-medium text-[#C8C8D6] uppercase tracking-wider"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody>
                  <tr onClick={() => navigate('/projects/1')} className="cursor-pointer border-t border-[#2E2E3F]/60 hover:bg-[#4A90E2]/10 transition-colors duration-300">
                    <td className="px-6 py-4 font-medium text-white whitespace-nowrap">E-commerce Platform Scan</td>
                    <td className="px-6 py-4 text-[#C8C8D6]">https://example-shop.com</td>
                    <td className="px-6 py-4 text-[#C8C8D6]">2023-10-26 14:30</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2.5">
                        <span className="h-2 w-2 rounded-full bg-[#00D1B2]"></span>
                        <span className="text-[#00D1B2]">Completed</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-white font-medium flex items-center gap-4">
                      <div className="flex items-center gap-2"><span className="text-[#FF4C4C]">5</span> <span className="text-[#C8C8D6] text-xs">Critical</span></div>
                      <div className="flex items-center gap-2"><span className="text-[#FFB833]">12</span> <span className="text-[#C8C8D6] text-xs">High</span></div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={(e) => { e.stopPropagation(); navigate('/projects/1'); }} className="text-[#C8C8D6] hover:text-[#4A90E2] transition-colors"><span className="material-symbols-outlined">open_in_new</span></button>
                    </td>
                  </tr>
                  <tr onClick={() => navigate('/projects/2')} className="cursor-pointer border-t border-[#2E2E3F]/60 hover:bg-[#4A90E2]/10 transition-colors duration-300">
                    <td className="px-6 py-4 font-medium text-white whitespace-nowrap">Corporate Website Audit</td>
                    <td className="px-6 py-4 text-[#C8C8D6]">https://ourbusiness.com</td>
                    <td className="px-6 py-4 text-[#C8C8D6]">2023-10-26 11:00</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2.5">
                        <span className="h-2 w-2 rounded-full bg-[#4A90E2]"></span>
                        <span className="text-[#4A90E2]">In Progress</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-white font-medium flex items-center gap-4">
                      <div className="flex items-center gap-2"><span className="text-[#FF4C4C]">2</span> <span className="text-[#C8C8D6] text-xs">Critical</span></div>
                      <div className="flex items-center gap-2"><span className="text-[#FFB833]">8</span> <span className="text-[#C8C8D6] text-xs">High</span></div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={(e) => { e.stopPropagation(); navigate('/projects/2'); }} className="text-[#C8C8D6] hover:text-[#4A90E2] transition-colors"><span className="material-symbols-outlined">open_in_new</span></button>
                    </td>
                  </tr>
                  <tr onClick={() => navigate('/projects/3')} className="cursor-pointer border-t border-[#2E2E3F]/60 hover:bg-[#4A90E2]/10 transition-colors duration-300">
                    <td className="px-6 py-4 font-medium text-white whitespace-nowrap">Marketing Landing Page</td>
                    <td className="px-6 py-4 text-[#C8C8D6]">https://promo.example.com</td>
                    <td className="px-6 py-4 text-[#C8C8D6]">2023-10-25 09:00</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2.5">
                        <span className="h-2 w-2 rounded-full bg-[#00D1B2]"></span>
                        <span className="text-[#00D1B2]">Completed</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-white font-medium flex items-center gap-4">
                      <div className="flex items-center gap-2"><span className="text-[#FF4C4C]">0</span> <span className="text-[#C8C8D6] text-xs">Critical</span></div>
                      <div className="flex items-center gap-2"><span className="text-[#FFB833]">1</span> <span className="text-[#C8C8D6] text-xs">High</span></div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={(e) => { e.stopPropagation(); navigate('/projects/3'); }} className="text-[#C8C8D6] hover:text-[#4A90E2] transition-colors"><span className="material-symbols-outlined">open_in_new</span></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="text-xs text-[#888888]">© 2024 SecureScan Dynamics. All rights reserved.</div>
        </div>
      </main>
    </div>
  );
};

export default ProjectListPage;