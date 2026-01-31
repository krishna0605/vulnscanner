'use client';

import Link from 'next/link';

export default function LandingPage() {
  return (
    <>
      {/* Background Elements */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-mesh-gradient opacity-60"></div>
      <div className="fixed top-[-20%] left-[-10%] w-[600px] h-[600px] bg-white/5 rounded-full blur-[120px] animate-drift"></div>
      <div
        className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-gray-500/10 rounded-full blur-[120px] animate-drift"
        style={{ animationDelay: '-5s' }}
      ></div>

      {/* Navigation */}
      <nav className="fixed w-full z-50 glass-nav transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex-shrink-0 flex items-center cursor-pointer group">
              <div className="relative w-10 h-10 mr-3 flex items-center justify-center">
                <span className="material-symbols-outlined text-white text-3xl absolute animate-pulse">
                  shield
                </span>
                <div className="absolute inset-0 bg-white/10 blur-lg rounded-full"></div>
              </div>
              <span className="font-sans font-bold text-xl tracking-tight text-white">
                Vuln<span className="text-slate-400">Scanner</span>
              </span>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-1">
                <Link
                  className="text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-full text-sm font-medium transition-all"
                  href="/features"
                >
                  Features
                </Link>
                <Link
                  className="text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-full text-sm font-medium transition-all"
                  href="/services"
                >
                  Services
                </Link>
                <Link
                  className="text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-full text-sm font-medium transition-all"
                  href="/pricing"
                >
                  Pricing
                </Link>
                <Link
                  className="text-slate-300 hover:text-white hover:bg-white/5 px-4 py-2 rounded-full text-sm font-medium transition-all"
                  href="/learn"
                >
                  Learn
                </Link>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-4">
              <Link
                href="/login"
                className="text-slate-300 hover:text-white px-4 py-2 text-sm font-mono font-medium hover:bg-white/5 rounded-lg transition-all"
              >
                LOG_IN
              </Link>
              <Link
                href="/signup"
                className="bg-white hover:bg-gray-100 text-black px-6 py-2 rounded-full text-sm font-bold shadow-glow hover:shadow-glow-hover transition-all transform hover:scale-105"
              >
                GET ACCESS
              </Link>
            </div>
            <div className="-mr-2 flex md:hidden">
              <button
                className="inline-flex items-center justify-center p-2 rounded-md text-slate-400 hover:text-white hover:bg-white/10 focus:outline-none"
                type="button"
              >
                <span className="sr-only">Open main menu</span>
                <span className="material-symbols-outlined">menu</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative pt-32 pb-16 sm:pt-48 sm:pb-32 overflow-hidden">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10 grid lg:grid-cols-2 gap-12 items-center">
          <div className="text-left">
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-white text-xs font-mono mb-6 backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-white mr-2 animate-pulse"></span>
              SYSTEM STATUS: SECURE
            </div>
            <h1 className="text-5xl sm:text-6xl md:text-7xl font-sans font-bold tracking-tight mb-6 leading-tight text-white">
              Secure Your <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-500 text-glow">
                Digital Frontier.
              </span>
            </h1>
            <p className="mt-4 max-w-lg text-lg text-slate-400 sm:text-xl font-light">
              Next-gen vulnerability scanning powered by autonomous AI agents. Comprehensive,
              actionable, and seamlessly integrated into your dev pipeline.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                className="px-8 py-4 rounded-full bg-white hover:bg-gray-200 text-black font-bold shadow-glow hover:shadow-glow-hover transition-all transform hover:-translate-y-1"
                href="/signup"
              >
                Start Scanning
              </Link>
              <a
                className="px-8 py-4 rounded-full bg-interactive-dark hover:bg-white/10 text-white font-medium backdrop-blur-md border border-white/10 transition-all flex items-center gap-2"
                href="#"
              >
                <span className="material-symbols-outlined text-sm">play_circle</span>
                Watch Demo
              </a>
            </div>
            <div className="mt-12 flex items-center gap-6 text-xs font-mono text-slate-500">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-white">check_circle</span>{' '}
                OWASP COMPLIANT
              </div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-white">bolt</span>{' '}
                REAL-TIME
              </div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-white">code</span> API
                FIRST
              </div>
            </div>
          </div>

          {/* Hero Visual */}
          <div className="relative h-[400px] w-full lg:h-[500px]">
            <div className="absolute inset-0 glass-panel rounded-[32px] overflow-hidden border border-white/10 p-4">
              <div className="h-full w-full bg-[#262626] rounded-2xl relative overflow-hidden flex flex-col">
                <div className="h-10 border-b border-white/5 flex items-center px-4 justify-between bg-white/5">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-white/30"></div>
                    <div className="w-3 h-3 rounded-full bg-white/30"></div>
                    <div className="w-3 h-3 rounded-full bg-white/30"></div>
                  </div>
                  <div className="text-[10px] font-mono text-slate-500">
                    LIVE THREAT MAP // V.2.4.0
                  </div>
                </div>
                <div className="flex-1 relative">
                  <div className="absolute inset-0 opacity-20 bg-[url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg')] bg-cover bg-center invert brightness-0"></div>
                  <div className="absolute top-[30%] left-[20%] w-2 h-2 bg-white rounded-full animate-ping"></div>
                  <div className="absolute top-[30%] left-[20%] w-2 h-2 bg-white rounded-full"></div>
                  <div className="absolute top-[45%] left-[60%] w-2 h-2 bg-gray-400 rounded-full animate-ping delay-700"></div>
                  <div className="absolute top-[45%] left-[60%] w-2 h-2 bg-white rounded-full delay-700"></div>
                  <div className="absolute top-[25%] left-[80%] w-2 h-2 bg-gray-300 rounded-full animate-ping delay-1000"></div>
                  <div className="absolute top-[25%] left-[80%] w-2 h-2 bg-white rounded-full delay-1000"></div>
                  <div
                    className="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent h-[10%] w-full animate-scan"
                    style={{ animation: 'scan 4s ease-in-out infinite' }}
                  ></div>
                </div>
                <div className="h-24 glass-panel border-t border-white/10 m-4 rounded-xl flex items-center justify-around p-2">
                  <div className="text-center">
                    <div className="text-[10px] font-mono text-slate-400">THREATS BLOCKED</div>
                    <div className="text-xl font-bold text-white">8,492</div>
                  </div>
                  <div className="w-px h-8 bg-white/10"></div>
                  <div className="text-center">
                    <div className="text-[10px] font-mono text-slate-400">UPTIME</div>
                    <div className="text-xl font-bold text-white">99.99%</div>
                  </div>
                  <div className="w-px h-8 bg-white/10"></div>
                  <div className="text-center">
                    <div className="text-[10px] font-mono text-slate-400">LATENCY</div>
                    <div className="text-xl font-bold text-white">12ms</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-gray-500/10 rounded-full blur-3xl"></div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-end mb-16">
            <div>
              <h2 className="text-4xl font-sans font-bold text-white mb-2">
                Why <span className="text-slate-400">VulnScanner?</span>
              </h2>
              <p className="text-slate-400 font-light max-w-md">
                Advanced capabilities designed for the modern stack.
              </p>
            </div>
            <div className="mt-4 md:mt-0">
              <a
                className="text-sm font-mono text-white hover:text-slate-300 transition-colors flex items-center gap-2"
                href="#"
              >
                VIEW_FULL_SPECS{' '}
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </a>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-4 gap-6 auto-rows-[200px]">
            <div className="glass-panel rounded-[32px] p-8 md:col-span-3 lg:col-span-2 md:row-span-2 bento-card relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                <span className="material-symbols-outlined text-[120px] text-white">shield</span>
              </div>
              <div className="relative z-10 h-full flex flex-col justify-between">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-gray-200 to-gray-500 flex items-center justify-center mb-6 shadow-glow">
                  <span className="material-symbols-outlined text-black text-3xl">shield</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-4">
                    Comprehensive Scanning Engine
                  </h3>
                  <p className="text-slate-400 leading-relaxed mb-6">
                    Our proprietary engine uses AI to identify zero-day vulnerabilities alongside
                    common CVEs. Covering SQLi, XSS, CSRF and more with 99.9% accuracy.
                  </p>
                  <ul className="space-y-2 font-mono text-xs text-slate-500">
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-white rounded-full"></span>{' '}
                      DEEP_PACKET_INSPECTION
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-white rounded-full"></span> HEURISTIC_ANALYSIS
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="glass-panel rounded-[32px] p-8 md:col-span-3 lg:col-span-2 md:row-span-1 bento-card flex flex-col justify-center group relative overflow-hidden">
              <div className="absolute -right-4 -bottom-4 w-32 h-32 bg-white/5 rounded-full blur-2xl group-hover:bg-white/10 transition-colors"></div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Actionable Reporting</h3>
                  <p className="text-slate-400 text-sm">
                    Prioritized fix recommendations, not just alerts.
                  </p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-interactive-dark flex items-center justify-center border border-white/10 group-hover:border-white/50 transition-colors">
                  <span className="material-symbols-outlined text-white">verified_user</span>
                </div>
              </div>
            </div>

            <div className="glass-panel rounded-[32px] p-6 md:col-span-2 lg:col-span-1 md:row-span-1 bento-card flex flex-col justify-between group">
              <div className="w-10 h-10 rounded-xl bg-interactive-dark flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white">
                  integration_instructions
                </span>
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">CI/CD Native</h3>
                <p className="text-slate-500 text-xs mt-2 font-mono">
                  PLUGINS: GITHUB, GITLAB, JENKINS
                </p>
              </div>
            </div>

            <div className="glass-panel rounded-[32px] p-6 md:col-span-2 lg:col-span-1 md:row-span-1 bento-card flex flex-col justify-between group">
              <div className="w-10 h-10 rounded-xl bg-interactive-dark flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white">speed</span>
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Lightning Fast</h3>
                <p className="text-slate-500 text-xs mt-2 font-mono">AVG SCAN TIME: &lt; 2 MIN</p>
              </div>
            </div>

            <div className="glass-panel rounded-[32px] p-8 md:col-span-2 lg:col-span-4 md:row-span-1 bento-card flex items-center justify-between group relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
              <div className="flex flex-col md:flex-row items-center gap-6 w-full">
                <div className="flex-shrink-0 w-16 h-16 rounded-full bg-section-dark flex items-center justify-center border border-interactive-dark">
                  <span className="material-symbols-outlined text-white text-3xl">
                    support_agent
                  </span>
                </div>
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-xl font-bold text-white">24/7 Expert Support</h3>
                  <p className="text-slate-400 text-sm">
                    Direct access to security engineers when you need critical help.
                  </p>
                </div>
                <button className="px-6 py-2 rounded-xl bg-interactive-dark hover:bg-white/20 text-white text-sm font-medium transition-colors border border-white/10">
                  Contact Support
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Educational Section */}
      <div className="py-24 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-24 items-center">
            <div className="mb-12 lg:mb-0 relative z-10">
              <div className="absolute -left-10 -top-10 w-32 h-32 bg-white/5 rounded-full blur-3xl"></div>
              <h2 className="text-4xl font-sans font-bold text-white mb-6">
                Understand the{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-gray-200 to-gray-500">
                  Threat Landscape
                </span>
              </h2>
              <p className="text-slate-300 mb-8 max-w-lg text-lg font-light leading-relaxed">
                See how modern vulnerabilities exploit system weaknesses. Our educational
                visualization engine breaks down complex attacks into understandable flows.
              </p>
              <div className="relative w-full aspect-video rounded-3xl overflow-hidden glass-panel border-white/10 group cursor-pointer shadow-2xl">
                <img
                  alt="Cybersecurity Visualization"
                  className="w-full h-full object-cover opacity-60 grayscale group-hover:opacity-40 transition-opacity duration-500 scale-105 group-hover:scale-100"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuCQbAhRKEybaDXnSUXNP0A964O9FHIc8_xu9OcPOVA-E6uHG8LcZ-WlQjTp90CtLe3ZSSKe6JmSoWOLzslFlnGsLF5FT8xdOioRsmYq18s1xFv6eCjtQaDjOPHyxeLaqY7exDRw-0CBNWQLPqLUj9pZxvHNz3gTaPYgUJLNklMoghznNSYppQgkYhFcdGZtGiimLZPZSlFYpkdKDmCvxVPHq3r4ZKo_lLxOrPU9S1_QnuZzXKnwt-jwV96zTpzTOC7yvC3yLM0h1-Y"
                />
                <div className="absolute inset-0 flex items-center justify-center z-20">
                  <div className="w-20 h-20 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-glow">
                    <span className="material-symbols-outlined text-white text-4xl ml-1">
                      play_arrow
                    </span>
                  </div>
                </div>
                <div className="absolute inset-0 grid grid-cols-6 grid-rows-4 opacity-20 pointer-events-none">
                  {Array(6)
                    .fill(null)
                    .map((_, i) => (
                      <div key={i} className="border-r border-white/30"></div>
                    ))}
                </div>
              </div>
            </div>

            <div className="space-y-6 relative z-10">
              <div className="glass-panel p-8 rounded-[24px] hover:border-white/30 transition-colors duration-300">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white">Key Concepts</h3>
                  <span className="material-symbols-outlined text-slate-500">school</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-xs font-mono text-white">
                    CIA_TRIAD
                  </span>
                  <span className="px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-xs font-mono text-white">
                    MFA
                  </span>
                  <span className="px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-xs font-mono text-white">
                    ENCRYPTION
                  </span>
                </div>
              </div>
              <div className="glass-panel p-8 rounded-[24px] hover:border-white/30 transition-colors duration-300">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white">Resources</h3>
                  <span className="material-symbols-outlined text-slate-500">library_books</span>
                </div>
                <p className="text-sm text-slate-400 mb-4 font-mono">
                  ACCESS_LEVEL: PUBLIC <br />
                  SOURCE: OWASP, NIST, MITRE
                </p>
                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-white w-2/3"></div>
                </div>
              </div>
              <div className="flex gap-4 pt-4">
                <button className="flex-1 py-4 px-6 rounded-2xl bg-interactive-dark border border-white/10 text-slate-300 font-medium hover:bg-white/10 hover:text-white transition-all text-sm font-mono tracking-wide">
                  EXPLORE_BASICS
                </button>
                <button className="flex-1 py-4 px-6 rounded-2xl bg-interactive-dark border border-white/10 text-slate-300 font-medium hover:bg-white/10 hover:text-white transition-all text-sm font-mono tracking-wide">
                  DEEP_DIVE_&gt;
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Core Services */}
      <div className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16 relative">
            <h2 className="text-4xl font-sans font-bold text-white mb-4">
              Core <span className="text-slate-400">Services</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-transparent via-white to-transparent mx-auto rounded-full"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10">
              <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white text-3xl">radar</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Automated Vulnerability Scans</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Continuously scan your applications for known vulnerabilities with scheduled
                automation.
              </p>
              <div className="flex items-center text-white text-xs font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                Learn more{' '}
                <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
              </div>
            </div>
            {/* ... other service cards ... */}
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10">
              <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white text-3xl">visibility</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Real-Time Monitoring</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Get instant alerts on new threats and suspicious activities across your network.
              </p>
              <div className="flex items-center text-white text-xs font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                Learn more{' '}
                <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10">
              <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white text-3xl">analytics</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Detailed Reports & Analytics</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Receive insightful reports to understand your security posture and trends over time.
              </p>
              <div className="flex items-center text-white text-xs font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                Learn more{' '}
                <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10">
              <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white text-3xl">hub</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Integration Ecosystem</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Connect with your favorite developer tools and platforms seamlessly.
              </p>
              <div className="flex items-center text-white text-xs font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                Learn more{' '}
                <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10">
              <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white text-3xl">gavel</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Compliance Assistance</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Streamline adherence to industry standards like PCI-DSS and GDPR effortlessly.
              </p>
              <div className="flex items-center text-white text-xs font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                Learn more{' '}
                <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10">
              <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-white text-3xl">build</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Guided Remediation</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Step-by-step guidance to help your team fix vulnerabilities fast and correctly.
              </p>
              <div className="flex items-center text-white text-xs font-bold uppercase tracking-wider opacity-0 group-hover:opacity-100 transition-opacity">
                Learn more{' '}
                <span className="material-symbols-outlined text-sm ml-1">arrow_forward</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Security Knowledge Base */}
      <div className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-sans font-bold text-white text-center mb-16">
            Security Knowledge Base
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="glass-panel rounded-[32px] p-10 border-t border-white/10 hover:border-white/50 transition-colors duration-500 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl group-hover:bg-white/10 transition-colors"></div>
              <div className="flex items-center mb-8 relative z-10">
                <div className="p-3 bg-interactive-dark rounded-xl mr-4 border border-white/10">
                  <span className="material-symbols-outlined text-white text-2xl">foundation</span>
                </div>
                <h3 className="text-2xl font-bold text-white">Core Principles</h3>
              </div>
              <ul className="space-y-4 relative z-10">
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    check_circle
                  </span>
                  Principle of Least Privilege
                </li>
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    check_circle
                  </span>
                  Secure Coding Practices
                </li>
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    check_circle
                  </span>
                  Continuous Patch Management
                </li>
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    check_circle
                  </span>
                  Multi-Factor Authentication (MFA)
                </li>
              </ul>
            </div>

            <div className="glass-panel rounded-[32px] p-10 border-t border-white/10 hover:border-gray-400/50 transition-colors duration-500 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-gray-400/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl group-hover:bg-gray-400/10 transition-colors"></div>
              <div className="flex items-center mb-8 relative z-10">
                <div className="p-3 bg-interactive-dark rounded-xl mr-4 border border-white/10">
                  <span className="material-symbols-outlined text-white text-2xl">
                    security_update_good
                  </span>
                </div>
                <h3 className="text-2xl font-bold text-white">Essential Precautions</h3>
              </div>
              <ul className="space-y-4 relative z-10">
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    shield_lock
                  </span>
                  Phishing & Social Engineering
                </li>
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    shield_lock
                  </span>
                  Secrets Management & Hygiene
                </li>
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    shield_lock
                  </span>
                  Reliable Data Backups
                </li>
                <li className="flex items-center text-sm text-slate-300 font-mono">
                  <span className="material-symbols-outlined text-white text-base mr-3">
                    shield_lock
                  </span>
                  Comprehensive Logging
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="py-24">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-[40px] p-12 sm:p-20 text-center shadow-glow border border-white/20 glass-panel">
            <div className="absolute inset-0 bg-gradient-to-br from-gray-700/30 via-gray-900/40 to-black/30 z-0"></div>
            <div className="absolute top-0 left-0 w-full h-full z-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]"></div>
            <div className="absolute -top-24 -left-24 w-64 h-64 bg-white/10 rounded-full blur-[80px]"></div>
            <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-gray-500/10 rounded-full blur-[80px]"></div>
            <div className="relative z-10">
              <h2 className="text-4xl sm:text-5xl font-sans font-bold text-white mb-6 text-glow">
                Ready to Secure
                <br />
                Your Applications?
              </h2>
              <p className="text-slate-300 mb-10 max-w-xl mx-auto text-lg font-light">
                Join thousands of developers and security professionals who trust VulnScanner.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                <a
                  className="w-full sm:w-auto px-10 py-4 rounded-full bg-white text-black font-bold hover:bg-gray-200 transition-all shadow-lg transform hover:-translate-y-1"
                  href="#"
                >
                  Start Free Trial
                </a>
                <a
                  className="w-full sm:w-auto px-10 py-4 rounded-full bg-transparent border border-white/30 text-white font-semibold hover:bg-white/10 transition-colors backdrop-blur-sm"
                  href="#"
                >
                  Talk to Sales
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-[#313131]/80 backdrop-blur-xl pt-20 pb-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-12 mb-16">
            <div className="col-span-2 md:col-span-2">
              <div className="flex items-center mb-6">
                <span className="material-symbols-outlined text-white text-3xl mr-2">security</span>
                <span className="font-sans font-bold text-2xl text-white">VulnScanner</span>
              </div>
              <p className="text-sm text-slate-400 max-w-xs font-light leading-relaxed">
                Protecting the modern web, one scan at a time. Enterprise-grade security for
                everyone.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-6 font-mono text-sm uppercase tracking-wider">
                Product
              </h4>
              <ul className="space-y-4 text-sm font-light">
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    Features
                  </a>
                </li>
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    Services
                  </a>
                </li>
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    Get Started
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-6 font-mono text-sm uppercase tracking-wider">
                Resources
              </h4>
              <ul className="space-y-4 text-sm font-light">
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    Learning Center
                  </a>
                </li>
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    Best Practices
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-6 font-mono text-sm uppercase tracking-wider">
                Company
              </h4>
              <ul className="space-y-4 text-sm font-light">
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    About
                  </a>
                </li>
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    Careers
                  </a>
                </li>
                <li>
                  <a className="text-slate-400 hover:text-white transition-colors" href="#">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-xs text-slate-500 text-center md:text-left font-mono">
              © 2024 VulnScanner. All rights reserved.
            </p>
            <div className="flex space-x-8 mt-4 md:mt-0 font-mono text-xs">
              <a className="text-slate-500 hover:text-white transition-colors" href="#">
                LEGAL
              </a>
              <a className="text-slate-500 hover:text-white transition-colors" href="#">
                PRIVACY
              </a>
              <a className="text-slate-500 hover:text-white transition-colors" href="#">
                TERMS
              </a>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
