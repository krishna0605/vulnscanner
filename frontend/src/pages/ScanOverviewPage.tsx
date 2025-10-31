import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const ScanOverviewPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen w-full bg-[#0A0B14] text-[#E0E0E0]">
      {/* Top navbar */}
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
              <Link to="/dashboard" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-white transition-all duration-300">
                <span className="material-symbols-outlined text-base">dashboard</span>
                Dashboard
              </Link>
              <Link to="/projects" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all duration-300">
                <span className="material-symbols-outlined text-base">folder</span>
                Projects
              </Link>
              <span className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#00FFFF] transition-all duration-300">
                <span className="material-symbols-outlined text-base">radar</span>
                Scans
              </span>
              <button type="button" aria-disabled="true" title="Coming soon" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all duration-300 cursor-not-allowed">
                <span className="material-symbols-outlined text-base">bar_chart</span>
                Reports
              </button>
              <button type="button" aria-disabled="true" title="Coming soon" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all duration-300 cursor-not-allowed">
                <span className="material-symbols-outlined text-base">settings</span>
                Settings
              </button>
            </nav>
          </div>
          <div className="flex flex-1 items-center justify-end gap-2 sm:gap-4">
            <button
              className="flex min-w-[140px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#00FFFF] text-black text-sm font-bold leading-normal tracking-[0.015em] hover:shadow-[0_0_10px_rgba(0,255,255,0.5)] transition-shadow"
              onClick={() => navigate('/scans/new')}
            >
              <span className="material-symbols-outlined mr-2 text-base">play_arrow</span>
              Start New Scan
            </button>
            <div
              className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border-2 border-[#00FFFF]/50"
              style={{
                backgroundImage:
                  'url("https://lh3.googleusercontent.com/aida-public/AB6AXuBW9yn3-oepu9ihgSD5Ac7Mtqxu3JtKlDpy2760YuJ9IepN-3VP0c67SghB3bMuBv_S7v6tWH3u28iw6DG-KzO2s_RBvNmFhl6sJ9N3_NxuuasqJ68s6Vflcue1XGQmHzV8CG4Y9H9vpfgJExh782b64C0WssJI7X6MJGNljF6YUkcFS3ChzbMR7wRR4Mp8m1PI-8_F8ag55ifvn7c0tg4eeTKG694K5YHOB1afFlSU1Tz39P14IV7oU8iVo3U80Ng0CcJB8KtvvcMz")',
              }}
            />
          </div>
        </div>
      </header>

      {/* Page content */}
      <main className="px-4 sm:px-10 flex flex-1 justify-center py-8">
        <div className="flex flex-col w-full max-w-6xl gap-8">
          <div className="flex flex-wrap justify-between gap-3 items-center">
            <h1 className="text-white text-3xl sm:text-4xl font-black leading-tight tracking-[-0.033em]">Scan Overview</h1>
          </div>

          {/* Active Scans */}
          <section className="flex flex-col gap-4">
            <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em] px-2 sm:px-4 pb-3 pt-5 border-b border-[#2E2E3F]/50">Active Scans</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-2 sm:p-4">
              {/* Card 1 */}
              <div className="flex flex-col gap-4 rounded-lg bg-[#131523] p-6 border border-[#2E2E3F]/50">
                <div className="flex justify-between items-start">
                  <div className="flex flex-col">
                    <p className="text-white text-lg font-bold leading-tight tracking-[-0.015em]">example-website.com</p>
                    <p className="text-[#FFBF00] text-sm">Scanning...</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="flex items-center justify-center size-8 rounded-full hover:bg-white/10 text-[#888888] hover:text-[#00FFFF] transition-colors" title="Pause"><span className="material-symbols-outlined text-xl">pause</span></button>
                    <button className="flex items-center justify-center size-8 rounded-full hover:bg-white/10 text-[#888888] hover:text-[#FF4C4C] transition-colors" title="Cancel"><span className="material-symbols-outlined text-xl">cancel</span></button>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-[#888888]">Progress</span>
                    <span className="text-sm font-medium text-[#00FFFF]">75%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-2.5">
                    <div className="bg-[#00FFFF] h-2.5 rounded-full" style={{ width: '75%' }}></div>
                  </div>
                </div>
              </div>
              {/* Card 2 */}
              <div className="flex flex-col gap-4 rounded-lg bg-[#131523] p-6 border border-[#2E2E3F]/50">
                <div className="flex justify-between items-start">
                  <div className="flex flex-col">
                    <p className="text-white text-lg font-bold leading-tight tracking-[-0.015em]">another-target.org</p>
                    <p className="text-[#666666] text-sm">Paused</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="flex items-center justify-center size-8 rounded-full hover:bg-white/10 text-[#888888] hover:text-[#00FFFF] transition-colors" title="Resume"><span className="material-symbols-outlined text-xl">play_arrow</span></button>
                    <button className="flex items-center justify-center size-8 rounded-full hover:bg-white/10 text-[#888888] hover:text-[#FF4C4C] transition-colors" title="Cancel"><span className="material-symbols-outlined text-xl">cancel</span></button>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-[#888888]">Progress</span>
                    <span className="text-sm font-medium text-[#00FFFF]">32%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-2.5">
                    <div className="bg-[#00FFFF] h-2.5 rounded-full" style={{ width: '32%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Scan History */}
          <section className="flex flex-col gap-4">
            <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em] px-2 sm:px-4 pb-3 pt-5 border-b border-[#2E2E3F]/50">Scan History</h2>
            <div className="p-2 sm:p-4">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#888888]">search</span>
                <input
                  className="w-full bg-[#131523] border border-[#2E2E3F]/50 rounded-lg pl-10 pr-4 py-2 text-[#E0E0E0] focus:ring-2 focus:ring-[#00FFFF] focus:border-[#00FFFF] transition-shadow"
                  placeholder="Filter by target URL or date..."
                  type="text"
                />
              </div>
            </div>
            <div className="overflow-x-auto p-2 sm:p-4">
              <table className="w-full text-sm text-left text-[#888888]">
                <thead className="text-xs text-[#E0E0E0] uppercase bg-[#131523]">
                  <tr>
                    <th scope="col" className="px-6 py-3 rounded-l-lg">Target</th>
                    <th scope="col" className="px-6 py-3">Date</th>
                    <th scope="col" className="px-6 py-3">Duration</th>
                    <th scope="col" className="px-6 py-3">Vulnerabilities</th>
                    <th scope="col" className="px-6 py-3 rounded-r-lg">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="bg-[#0A0B14] border-b border-[#131523] hover:bg-[#131523]/50 cursor-pointer">
                    <th scope="row" className="px-6 py-4 font-medium text-white whitespace-nowrap">secure-api.dev</th>
                    <td className="px-6 py-4">2024-05-20 14:30</td>
                    <td className="px-6 py-4">12m 45s</td>
                    <td className="px-6 py-4"><span className="text-[#FF4C4C] font-bold">5 Critical</span>, 12 Medium</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="size-2.5 rounded-full bg-[#FF4C4C]"></div>
                        <span>Critical Found</span>
                      </div>
                    </td>
                  </tr>
                  <tr className="bg-[#0A0B14] border-b border-[#131523] hover:bg-[#131523]/50 cursor-pointer">
                    <th scope="row" className="px-6 py-4 font-medium text-white whitespace-nowrap">e-commerce-store.com</th>
                    <td className="px-6 py-4">2024-05-19 09:15</td>
                    <td className="px-6 py-4">25m 10s</td>
                    <td className="px-6 py-4"><span className="text-[#FFBF00] font-bold">8 Medium</span>, 22 Low</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="size-2.5 rounded-full bg-[#FFBF00]"></div>
                        <span>Warnings</span>
                      </div>
                    </td>
                  </tr>
                  <tr className="bg-[#0A0B14] border-b border-[#131523] hover:bg-[#131523]/50 cursor-pointer">
                    <th scope="row" className="px-6 py-4 font-medium text-white whitespace-nowrap">my-blog-project.net</th>
                    <td className="px-6 py-4">2024-05-18 22:00</td>
                    <td className="px-6 py-4">8m 02s</td>
                    <td className="px-6 py-4">3 Low</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="size-2.5 rounded-full bg-[#00FF7F]"></div>
                        <span>Completed</span>
                      </div>
                    </td>
                  </tr>
                  <tr className="bg-[#0A0B14] hover:bg-[#131523]/50 cursor-pointer">
                    <th scope="row" className="px-6 py-4 font-medium text-white whitespace-nowrap">test-env.internal</th>
                    <td className="px-6 py-4">2024-05-17 11:45</td>
                    <td className="px-6 py-4">2m 15s</td>
                    <td className="px-6 py-4">N/A</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="size-2.5 rounded-full bg-[#666666]"></div>
                        <span>Cancelled</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default ScanOverviewPage;