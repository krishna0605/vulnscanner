'use client';

import Link from 'next/link';

export default function LearnPage() {
  return (
    <>
      {/* Background Elements */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div
        className="fixed inset-0 w-full h-full -z-20 bg-stealth-gradient opacity-80"
        style={{
          backgroundImage: 'linear-gradient(135deg, #313131 0%, #414141 50%, #313131 100%)',
        }}
      ></div>
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
                  className="text-white bg-white/10 px-4 py-2 rounded-full text-sm font-medium transition-all shadow-glow"
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

      <div className="relative pt-32 pb-16 overflow-hidden">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10 text-center">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-white text-xs font-mono mb-6 backdrop-blur-md">
            <span className="material-symbols-outlined text-sm mr-2">school</span>
            KNOWLEDGE BASE
          </div>
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-sans font-bold tracking-tight mb-6 leading-tight text-white">
            Security{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-500 text-glow">
              Academy
            </span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-slate-400 sm:text-xl font-light">
            Master the art of cybersecurity. From basic vulnerabilities to advanced exploit chains,
            our curated resources will level up your skills.
          </p>
        </div>
      </div>

      <div className="py-12 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* Sidebar / filter (mockup for visual consistency) */}
            <div className="lg:col-span-3 hidden lg:block">
              <div className="sticky top-32 glass-panel p-6 rounded-2xl border border-white/10">
                <h3 className="font-bold text-white mb-6 tracking-wide text-sm font-mono uppercase">
                  Topics
                </h3>
                <ul className="space-y-3 text-sm">
                  <li>
                    <a
                      href="#"
                      className="flex items-center justify-between text-white font-medium bg-white/10 px-3 py-2 rounded-lg"
                    >
                      All Resources{' '}
                      <span className="text-xs bg-white text-black px-1.5 rounded-full">42</span>
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="flex items-center justify-between text-slate-400 hover:text-white hover:bg-white/5 px-3 py-2 rounded-lg transition-colors"
                    >
                      OWASP Top 10{' '}
                      <span className="text-xs bg-white/10 text-slate-300 px-1.5 rounded-full">
                        12
                      </span>
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="flex items-center justify-between text-slate-400 hover:text-white hover:bg-white/5 px-3 py-2 rounded-lg transition-colors"
                    >
                      Network Security{' '}
                      <span className="text-xs bg-white/10 text-slate-300 px-1.5 rounded-full">
                        8
                      </span>
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="flex items-center justify-between text-slate-400 hover:text-white hover:bg-white/5 px-3 py-2 rounded-lg transition-colors"
                    >
                      Cloud Security{' '}
                      <span className="text-xs bg-white/10 text-slate-300 px-1.5 rounded-full">
                        15
                      </span>
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="flex items-center justify-between text-slate-400 hover:text-white hover:bg-white/5 px-3 py-2 rounded-lg transition-colors"
                    >
                      Secure Coding{' '}
                      <span className="text-xs bg-white/10 text-slate-300 px-1.5 rounded-full">
                        7
                      </span>
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            {/* Main Content Grid */}
            <div className="lg:col-span-9">
              {/* Featured Article */}
              <div className="glass-panel p-0 rounded-[32px] border border-white/10 overflow-hidden group hover:shadow-glow transition-all duration-300 mb-12">
                <div className="grid md:grid-cols-2 relative">
                  <div className="h-64 md:h-auto overflow-hidden">
                    <img
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuDQe5XGaK3XLds7gTMQvAArEDTScqYCM2SP0AkpOfhkA6yuIED_68FNindcJq8q-s_SpMCT4zWkJ3wwbP62pCTUnoeqWYmzcbZIieStpuyNKR4AzrLQ4kHlAB8xm371-3sWyO5mUUSQo4ZVPFEldOPhLCGydaYSwP4MZXCS20KeqpXME4FQ-X9R96DpXtceCkpGv4TopTnvzEruATqEmoV4GyvEtZbukhujHLrQHjlYZwjkdnwe4PKnxQRp1U0maHadqz0V20AwjrU"
                      alt="Featured"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-black/80 to-transparent"></div>
                  </div>
                  <div className="p-8 md:p-12 flex flex-col justify-center">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="bg-red-500/20 text-red-300 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wide border border-red-500/20">
                        Critical
                      </span>
                      <span className="text-slate-400 text-xs font-mono">5 MIN READ</span>
                    </div>
                    <h2 className="text-3xl font-bold text-white mb-4 group-hover:text-blue-200 transition-colors">
                      Understanding Log4j: A Deep Dive
                    </h2>
                    <p className="text-slate-400 mb-8 leading-relaxed line-clamp-3">
                      The Log4Shell vulnerability shook the internet. In this deep dive, we explore
                      how the exploit works at the packet level, why it was so widespread, and how
                      to ensuring your Java applications are permanently patched against JNDI
                      injection attacks.
                    </p>
                    <a
                      href="#"
                      className="inline-flex items-center text-white font-bold hover:text-gray-300"
                    >
                      Read Article{' '}
                      <span className="material-symbols-outlined ml-2 group-hover:translate-x-1 transition-transform">
                        arrow_forward
                      </span>
                    </a>
                  </div>
                </div>
              </div>

              {/* Article Grid */}
              <div className="grid md:grid-cols-2 gap-8">
                {/* Article 1 */}
                <div className="glass-panel rounded-3xl overflow-hidden border border-white/5 hover:border-white/20 transition-all duration-300 group flex flex-col">
                  <div className="h-48 overflow-hidden relative">
                    <img
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuCQbAhRKEybaDXnSUXNP0A964O9FHIc8_xu9OcPOVA-E6uHG8LcZ-WlQjTp90CtLe3ZSSKe6JmSoWOLzslFlnGsLF5FT8xdOioRsmYq18s1xFv6eCjtQaDjOPHyxeLaqY7exDRw-0CBNWQLPqLUj9pZxvHNz3gTaPYgUJLNklMoghznNSYppQgkYhFcdGZtGiimLZPZSlFYpkdKDmCvxVPHq3r4ZKo_lLxOrPU9S1_QnuZzXKnwt-jwV96zTpzTOC7yvC3yLM0h1-Y"
                      alt="Article"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-80 group-hover:opacity-100"
                    />
                  </div>
                  <div className="p-8 flex-grow flex flex-col">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-blue-400 text-xs font-bold uppercase tracking-wide">
                        Tutorial
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">
                      Securing React Applications
                    </h3>
                    <p className="text-slate-400 text-sm mb-6 flex-grow">
                      Common XSS pitfalls in modern frontend frameworks and how to avoid them using
                      proper sanitization.
                    </p>
                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-gray-600"></div>
                        <span className="text-xs text-slate-400">Alex Chen</span>
                      </div>
                      <span className="text-xs text-slate-500">Dec 12, 2023</span>
                    </div>
                  </div>
                </div>

                {/* Article 2 */}
                <div className="glass-panel rounded-3xl overflow-hidden border border-white/5 hover:border-white/20 transition-all duration-300 group flex flex-col">
                  <div className="h-48 overflow-hidden relative">
                    <img
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuBrh8JoiDcDiX-83P0flM430YFkBK8maFmOYDPASJq6ONgbzdYREkyNRy94G5McST6DvmTJYS7ah3YyDdCzSHwp0BizCPfg9yJwsRs_uQ7MrHLLMAJzaW3g6V51j4sSDXUekt1_nwNPNFlim2g7uU--gc0jyJnWVzj-zofTSEd6RfJa2isKmCMZc37c3YC9FKnzOl4RCgpZaDn3Fk2HL6l5Rl09vaxl-kBGh1wk38ZgZOj9nI4PKKUely8pz9nAfLT058v5yjSWKi4"
                      alt="Article"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-80 group-hover:opacity-100"
                    />
                  </div>
                  <div className="p-8 flex-grow flex flex-col">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-green-400 text-xs font-bold uppercase tracking-wide">
                        Guide
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">Zero Trust Architecture</h3>
                    <p className="text-slate-400 text-sm mb-6 flex-grow">
                      Implenting &apos;never trust, always verify&apos; principles in a legacy
                      monolithic environment.
                    </p>
                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-gray-600"></div>
                        <span className="text-xs text-slate-400">Sarah Jones</span>
                      </div>
                      <span className="text-xs text-slate-500">Nov 28, 2023</span>
                    </div>
                  </div>
                </div>

                {/* Article 3 */}
                <div className="glass-panel rounded-3xl overflow-hidden border border-white/5 hover:border-white/20 transition-all duration-300 group flex flex-col">
                  <div className="h-48 overflow-hidden relative">
                    <img
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuB0UJR0BArUmh622Mnd9bOeQeFEl_Sg7A7ij7ezeJwkDHMldtFQIDnwdHV2gfCh04lgQAPcXzTun2l00EKhqviZjkzfuiGl29v64OxkKZkxKA7rZnhm3tdCV12_mficKhM7AiU3khK0RrLru8QwbqVo9pqGr55Go4gJHCnAQnlFYHvkOB4nm-zisI9npO6vqhl6IW3kKTgro5_L1Fd0VEITnUoFvyM4NahyvoEAoIzbHKC8rLhPk0jA7H3C1vckow5oEGkdN4V7wPY"
                      alt="Article"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-80 group-hover:opacity-100"
                    />
                  </div>
                  <div className="p-8 flex-grow flex flex-col">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-purple-400 text-xs font-bold uppercase tracking-wide">
                        Research
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">
                      The Future of AI in Security
                    </h3>
                    <p className="text-slate-400 text-sm mb-6 flex-grow">
                      How large language models are changing both offense and defense in
                      cybersecurity.
                    </p>
                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-gray-600"></div>
                        <span className="text-xs text-slate-400">Dr. M. Ali</span>
                      </div>
                      <span className="text-xs text-slate-500">Oct 15, 2023</span>
                    </div>
                  </div>
                </div>

                {/* Article 4 */}
                <div className="glass-panel rounded-3xl overflow-hidden border border-white/5 hover:border-white/20 transition-all duration-300 group flex flex-col">
                  <div className="h-48 overflow-hidden relative">
                    {/* Placeholder gradient as image */}
                    <div className="w-full h-full bg-gradient-to-br from-indigo-900 to-purple-900 group-hover:scale-105 transition-transform duration-500"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="material-symbols-outlined text-white/50 text-5xl">code</span>
                    </div>
                  </div>
                  <div className="p-8 flex-grow flex flex-col">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-blue-400 text-xs font-bold uppercase tracking-wide">
                        Tutorial
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">
                      Intro to Binary Exploitation
                    </h3>
                    <p className="text-slate-400 text-sm mb-6 flex-grow">
                      Buffer overflows explained simply. A starting point for aspiring reverse
                      engineers.
                    </p>
                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-gray-600"></div>
                        <span className="text-xs text-slate-400">J. Smith</span>
                      </div>
                      <span className="text-xs text-slate-500">Sep 02, 2023</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Pagination */}
              <div className="mt-16 flex justify-center">
                <nav className="flex items-center gap-2">
                  <button
                    className="w-10 h-10 rounded-lg flex items-center justify-center border border-white/10 text-white hover:bg-white/10 transition-colors disabled:opacity-50"
                    disabled
                  >
                    <span className="material-symbols-outlined text-sm">chevron_left</span>
                  </button>
                  <button className="w-10 h-10 rounded-lg flex items-center justify-center bg-white text-black font-bold">
                    1
                  </button>
                  <button className="w-10 h-10 rounded-lg flex items-center justify-center border border-white/10 text-white hover:bg-white/10 transition-colors">
                    2
                  </button>
                  <button className="w-10 h-10 rounded-lg flex items-center justify-center border border-white/10 text-white hover:bg-white/10 transition-colors">
                    3
                  </button>
                  <button className="w-10 h-10 rounded-lg flex items-center justify-center border border-white/10 text-white hover:bg-white/10 transition-colors">
                    <span className="material-symbols-outlined text-sm">chevron_right</span>
                  </button>
                </nav>
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
