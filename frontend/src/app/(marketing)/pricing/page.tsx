'use client';

import Link from 'next/link';

export default function PricingPage() {
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
                  className="text-white bg-white/10 px-4 py-2 rounded-full text-sm font-medium transition-all shadow-glow"
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

      <div className="relative pt-40 pb-20 sm:pt-48 sm:pb-32 overflow-hidden">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10 text-center">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-white text-xs font-mono mb-6 backdrop-blur-md">
            <span className="material-symbols-outlined text-sm mr-2">savings</span>
            TRANSPARENT PRICING
          </div>
          <h1 className="text-5xl sm:text-7xl font-sans font-bold tracking-tight mb-6 leading-tight text-white">
            Secure Your Stack,
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-500 text-glow">
              Not Your Budget.
            </span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-slate-400 sm:text-xl font-light">
            Simple, predictable pricing for companies of all sizes. No hidden fees or per-seat
            limits.
          </p>

          <div className="flex justify-center mt-10">
            <div className="glass-panel p-1 rounded-full inline-flex relative">
              <div className="w-36 absolute left-1 top-1 bottom-1 bg-white rounded-full transition-all duration-300 transform translate-x-0"></div>
              <button className="relative z-10 w-36 py-2 text-sm font-bold text-black rounded-full transition-colors flex justify-center items-center">
                Monthly
              </button>
              <button className="relative z-10 w-36 py-2 text-sm font-bold text-slate-400 hover:text-white transition-colors flex justify-center items-center">
                Yearly <span className="text-[10px] text-green-400 ml-1">-20%</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="py-12 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Starter Plan */}
            <div className="glass-panel rounded-[32px] p-8 border border-white/10 hover:border-white/20 transition-all duration-300 group relative flex flex-col h-full">
              <h3 className="text-xl font-bold text-white mb-2">Starter</h3>
              <div className="flex items-baseline mb-6">
                <span className="text-4xl font-bold text-white">$0</span>
                <span className="text-slate-400 ml-2">/month</span>
              </div>
              <p className="text-sm text-slate-400 mb-8 h-10">
                Perfect for individuals and hobby projects.
              </p>
              <button className="w-full py-3 rounded-xl border border-white/20 text-white hover:bg-white hover:text-black transition-all font-bold mb-8">
                Start Free
              </button>
              <ul className="space-y-4 text-sm text-slate-300 mt-auto">
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>Daily automated scans</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>1 Project limit</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>Community support</span>
                </li>
                <li className="flex items-center gap-3 opacity-50">
                  <span className="material-symbols-outlined text-sm">close</span>
                  <span>Real-time alerts</span>
                </li>
                <li className="flex items-center gap-3 opacity-50">
                  <span className="material-symbols-outlined text-sm">close</span>
                  <span>API access</span>
                </li>
              </ul>
            </div>

            {/* Professional Plan */}
            <div className="glass-panel rounded-[32px] p-8 border border-white/30 bg-white/5 relative shadow-glow z-10 overflow-hidden flex flex-col h-full border-t-4 border-t-purple-500">
              <div className="absolute top-4 right-4 bg-white text-black text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wide">
                Most Popular
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Professional</h3>
              <div className="flex items-baseline mb-6">
                <span className="text-4xl font-bold text-white">$49</span>
                <span className="text-slate-400 ml-2">/month</span>
              </div>
              <p className="text-sm text-slate-400 mb-8 h-10">
                For growing teams and startups shipping fast.
              </p>
              <button className="w-full py-3 rounded-xl bg-white text-black hover:bg-gray-200 transition-all font-bold mb-8 shadow-lg">
                Get Started
              </button>
              <ul className="space-y-4 text-sm text-slate-300 mt-auto">
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-green-400 text-sm">check</span>
                  <span>Continuous monitoring</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-green-400 text-sm">check</span>
                  <span>10 Projects limit</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-green-400 text-sm">check</span>
                  <span>Real-time Slack/Email alerts</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-green-400 text-sm">check</span>
                  <span>API access & Webhooks</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-green-400 text-sm">check</span>
                  <span>7-day data retention</span>
                </li>
              </ul>
            </div>

            {/* Enterprise Plan */}
            <div className="glass-panel rounded-[32px] p-8 border border-white/10 hover:border-white/20 transition-all duration-300 group relative flex flex-col h-full">
              <h3 className="text-xl font-bold text-white mb-2">Enterprise</h3>
              <div className="flex items-baseline mb-6">
                <span className="text-4xl font-bold text-white">Custom</span>
              </div>
              <p className="text-sm text-slate-400 mb-8 h-10">
                Advanced security and compliance for large orgs.
              </p>
              <button className="w-full py-3 rounded-xl bg-interactive-dark border border-white/10 text-white hover:bg-white/20 transition-all font-bold mb-8">
                Contact Sales
              </button>
              <ul className="space-y-4 text-sm text-slate-300 mt-auto">
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>Unlimited projects</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>SSO & RBAC</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>Dedicated success manager</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>Custom contract & SLAs</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-white text-sm">check</span>
                  <span>On-premise deployment option</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="py-24 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-sans font-bold text-white mb-12">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4 text-left">
            <div className="glass-panel p-6 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
              <h4 className="text-lg font-bold text-white mb-2">
                Can I cancel my subscription at any time?
              </h4>
              <p className="text-slate-400 text-sm leading-relaxed">
                Yes, you can cancel or downgrade your plan at any time from your dashboard. Changes
                will take effect at the end of your current billing cycle.
              </p>
            </div>
            <div className="glass-panel p-6 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
              <h4 className="text-lg font-bold text-white mb-2">
                What counts as a &quot;Project&quot;?
              </h4>
              <p className="text-slate-400 text-sm leading-relaxed">
                A project involves a single repository or top-level URL (e.g., example.com) and its
                subdomains. You can scan multiple environments (staging, prod) within one project.
              </p>
            </div>
            <div className="glass-panel p-6 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
              <h4 className="text-lg font-bold text-white mb-2">
                Do you offer a free trial for the Professional plan?
              </h4>
              <p className="text-slate-400 text-sm leading-relaxed">
                Yes, we offer a 14-day full-feature free trial for the Professional plan. No credit
                card required to start.
              </p>
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
