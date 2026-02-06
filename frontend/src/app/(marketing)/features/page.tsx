'use client';

import Link from 'next/link';

export default function FeaturesPage() {
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
            <Link href="/" className="flex-shrink-0 flex items-center cursor-pointer group">
              <div className="relative w-10 h-10 mr-3 flex items-center justify-center">
                <span className="material-symbols-outlined text-white text-3xl absolute animate-pulse">
                  shield
                </span>
                <div className="absolute inset-0 bg-white/10 blur-lg rounded-full"></div>
              </div>
              <span className="font-sans font-bold text-xl tracking-tight text-white">
                Vuln<span className="text-slate-400">Scanner</span>
              </span>
            </Link>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-1">
                <Link
                  className="text-white bg-white/10 px-4 py-2 rounded-full text-sm font-medium transition-all"
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

      <div className="relative pt-48 pb-20 sm:pt-60 sm:pb-32 overflow-hidden text-center">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-white text-xs font-mono mb-8 backdrop-blur-md">
            <span className="material-symbols-outlined text-sm mr-2">hub</span>
            PLATFORM CAPABILITIES V2.4
          </div>
          <h1 className="text-5xl sm:text-7xl font-sans font-bold tracking-tight mb-8 leading-tight text-white">
            Security Deep Dive.
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-500 text-glow">
              Uncompromised Power.
            </span>
          </h1>
          <p className="mt-4 text-lg text-slate-400 sm:text-xl font-light max-w-2xl mx-auto">
            Explore the core technologies that make VulnScanner the industry leader in autonomous
            vulnerability management.
          </p>
        </div>
      </div>

      <div className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="text-left order-2 lg:order-1">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-700 to-black border border-white/10 flex items-center justify-center mb-8 shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">sensors</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-sans font-bold text-white mb-6">
                Automated Scanning Engine
              </h2>
              <p className="text-slate-400 text-lg leading-relaxed mb-8">
                Our AI-driven scanning engine works tirelessly in the background, identifying
                vulnerabilities across your entire stack. From static code analysis to dynamic
                application testing, we cover every angle without manual intervention.
              </p>
              <ul className="space-y-4 font-mono text-sm text-slate-300">
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Zero-configuration continuous deployment</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Heuristic analysis for zero-day threats</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Multi-vector attack simulation</span>
                </li>
              </ul>
              <div className="mt-10">
                <a
                  className="text-white border-b border-white hover:border-gray-400 pb-1 transition-colors inline-flex items-center font-mono text-sm"
                  href="#"
                >
                  VIEW_SCANNER_DOCS{' '}
                  <span className="material-symbols-outlined text-sm ml-2">arrow_forward</span>
                </a>
              </div>
            </div>
            <div className="relative order-1 lg:order-2 group">
              <div className="glass-panel rounded-[32px] p-2 border border-white/10 overflow-hidden transform transition-all duration-700 hover:scale-[1.02] hover:shadow-glow">
                <div className="relative rounded-[28px] overflow-hidden aspect-[4/3]">
                  <img
                    alt="Abstract Data Mesh"
                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-500"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuDQe5XGaK3XLds7gTMQvAArEDTScqYCM2SP0AkpOfhkA6yuIED_68FNindcJq8q-s_SpMCT4zWkJ3wwbP62pCTUnoeqWYmzcbZIieStpuyNKR4AzrLQ4kHlAB8xm371-3sWyO5mUUSQo4ZVPFEldOPhLCGydaYSwP4MZXCS20KeqpXME4FQ-X9R96DpXtceCkpGv4TopTnvzEruATqEmoV4GyvEtZbukhujHLrQHjlYZwjkdnwe4PKnxQRp1U0maHadqz0V20AwjrU"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-background-dark/80 to-transparent"></div>
                  <div className="absolute bottom-6 left-6 right-6">
                    <div className="glass-panel p-4 rounded-xl flex items-center justify-between border border-white/20">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                        <span className="text-xs font-mono text-white">SCANNING_COMPLETE</span>
                      </div>
                      <span className="text-xs font-mono text-slate-400">98.2% COVERAGE</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -z-10 -right-10 -top-10 w-64 h-64 bg-white/5 rounded-full blur-[80px]"></div>
            </div>
          </div>
        </div>
      </div>

      <div className="py-24 relative bg-section-dark/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="relative order-1 group">
              <div className="glass-panel rounded-[32px] p-2 border border-white/10 overflow-hidden transform transition-all duration-700 hover:scale-[1.02] hover:shadow-glow">
                <div className="relative rounded-[28px] overflow-hidden aspect-[4/3]">
                  <img
                    alt="Real Time Monitoring"
                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-500"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuBrh8JoiDcDiX-83P0flM430YFkBK8maFmOYDPASJq6ONgbzdYREkyNRy94G5McST6DvmTJYS7ah3YyDdCzSHwp0BizCPfg9yJwsRs_uQ7MrHLLMAJzaW3g6V51j4sSDXUekt1_nwNPNFlim2g7uU--gc0jyJnWVzj-zofTSEd6RfJa2isKmCMZc37c3YC9FKnzOl4RCgpZaDn3Fk2HL6l5Rl09vaxl-kBGh1wk38ZgZOj9nI4PKKUely8pz9nAfLT058v5yjSWKi4"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-background-dark/90 via-transparent to-transparent"></div>
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-xs space-y-3">
                    <div
                      className="glass-panel p-4 rounded-xl border-l-4 border-red-500 flex gap-4 backdrop-blur-xl animate-drift"
                      style={{ animationDuration: '6s' }}
                    >
                      <span className="material-symbols-outlined text-red-400">warning</span>
                      <div>
                        <div className="text-xs font-bold text-white mb-1">
                          SQL Injection Attempt
                        </div>
                        <div className="text-[10px] font-mono text-slate-400">
                          IP: 192.168.1.45 • BLOCKED
                        </div>
                      </div>
                    </div>
                    <div
                      className="glass-panel p-4 rounded-xl border-l-4 border-yellow-500 flex gap-4 backdrop-blur-xl animate-drift"
                      style={{ animationDuration: '7s', animationDelay: '1s' }}
                    >
                      <span className="material-symbols-outlined text-yellow-400">visibility</span>
                      <div>
                        <div className="text-xs font-bold text-white mb-1">Anomalous Traffic</div>
                        <div className="text-[10px] font-mono text-slate-400">
                          /api/v1/users • FLAGGED
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -z-10 -left-10 -bottom-10 w-64 h-64 bg-interactive-dark/20 rounded-full blur-[80px]"></div>
            </div>
            <div className="text-left order-2">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-700 to-black border border-white/10 flex items-center justify-center mb-8 shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">
                  notifications_active
                </span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-sans font-bold text-white mb-6">
                Real-time Intelligence
              </h2>
              <p className="text-slate-400 text-lg leading-relaxed mb-8">
                Don&apos;t wait for weekly reports. Our real-time alert system pushes critical
                security notifications to your team instantly via Slack, PagerDuty, or Email. React
                to threats as they happen, not after the damage is done.
              </p>
              <ul className="space-y-4 font-mono text-sm text-slate-300">
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Sub-second latency detection</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Smart noise reduction AI</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Customizable severity thresholds</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="text-left order-2 lg:order-1">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-700 to-black border border-white/10 flex items-center justify-center mb-8 shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">webhook</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-sans font-bold text-white mb-6">
                API Security Shield
              </h2>
              <p className="text-slate-400 text-lg leading-relaxed mb-8">
                APIs are the new attack surface. We provide dedicated protection for your endpoints,
                ensuring that only legitimate traffic gets through. Automatically generate schemas
                and validate every request against your OpenAPI specifications.
              </p>
              <ul className="space-y-4 font-mono text-sm text-slate-300">
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Schema conformance validation</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Broken Object Level Authorization (BOLA) checks</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white">check_circle</span>
                  <span>Rate limiting and throttling analysis</span>
                </li>
              </ul>
            </div>
            <div className="relative order-1 lg:order-2 group">
              <div className="glass-panel rounded-[32px] p-2 border border-white/10 overflow-hidden transform transition-all duration-700 hover:scale-[1.02] hover:shadow-glow">
                <div className="relative rounded-[28px] overflow-hidden aspect-[4/3]">
                  <img
                    alt="Abstract API Network"
                    className="w-full h-full object-cover opacity-60 grayscale group-hover:opacity-80 transition-opacity duration-500"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuB0UJR0BArUmh622Mnd9bOeQeFEl_Sg7A7ij7ezeJwkDHMldtFQIDnwdHV2gfCh04lgQAPcXzTun2l00EKhqviZjkzfuiGl29v64OxkKZkxKA7rZnhm3tdCV12_mficKhM7AiU3khK0RrLru8QwbqVo9pqGr55Go4gJHCnAQnlFYHvkOB4nm-zisI9npO6vqhl6IW3kKTgro5_L1Fd0VEITnUoFvyM4NahyvoEAoIzbHKC8rLhPk0jA7H3C1vckow5oEGkdN4V7wPY"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-background-dark via-transparent to-transparent"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="relative w-40 h-40">
                      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-16 h-16 bg-white/10 rounded-full border border-white/30 backdrop-blur-md flex items-center justify-center z-20 shadow-glow">
                        <span className="material-symbols-outlined text-white">dns</span>
                      </div>
                      <div className="absolute bottom-0 left-0 w-12 h-12 bg-interactive-dark rounded-full border border-white/20 backdrop-blur-md flex items-center justify-center z-10">
                        <span className="material-symbols-outlined text-slate-300 text-sm">
                          smartphone
                        </span>
                      </div>
                      <div className="absolute bottom-0 right-0 w-12 h-12 bg-interactive-dark rounded-full border border-white/20 backdrop-blur-md flex items-center justify-center z-10">
                        <span className="material-symbols-outlined text-slate-300 text-sm">
                          laptop
                        </span>
                      </div>
                      {/* SVG line graph fix */}
                      <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                        <line
                          stroke="rgba(255,255,255,0.2)"
                          strokeDasharray="4"
                          strokeWidth="2"
                          x1="50%"
                          x2="20%"
                          y1="20%"
                          y2="80%"
                        ></line>
                        <line
                          stroke="rgba(255,255,255,0.2)"
                          strokeDasharray="4"
                          strokeWidth="2"
                          x1="50%"
                          x2="80%"
                          y1="20%"
                          y2="80%"
                        ></line>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -z-10 -right-10 bottom-10 w-64 h-64 bg-white/5 rounded-full blur-[80px]"></div>
            </div>
          </div>
        </div>
      </div>

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
