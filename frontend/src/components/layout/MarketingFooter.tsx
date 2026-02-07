'use client';

import Link from 'next/link';

export default function MarketingFooter() {
  return (
    <footer className="border-t border-white/10 bg-[#313131]/80 backdrop-blur-xl pt-20 pb-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-16">
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
                <Link className="text-slate-400 hover:text-white transition-colors" href="/features">
                  Features
                </Link>
              </li>
              <li>
                <Link className="text-slate-400 hover:text-white transition-colors" href="/services">
                  Services
                </Link>
              </li>
              <li>
                <Link className="text-slate-400 hover:text-white transition-colors" href="/signup">
                  Get Started
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-white mb-6 font-mono text-sm uppercase tracking-wider">
              Resources
            </h4>
            <ul className="space-y-4 text-sm font-light">
              <li>
                <Link className="text-slate-400 hover:text-white transition-colors" href="/learn">
                  Learning Center
                </Link>
              </li>
              <li>
                <a 
                  className="text-slate-400 hover:text-white transition-colors" 
                  href="https://healthdocliv.notion.site/USER_GUIDE-300c54ff4fff80f6ab40d3f140abf748"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  User Guide
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-xs text-slate-500 text-center md:text-left font-mono">
            © 2024 VulnScanner. All rights reserved. Created by{' '}
            <a 
              href="https://creative-engineer.dev/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition-colors"
            >
              Krishna Kapoor
            </a>
          </p>
          <div className="flex space-x-8 mt-4 md:mt-0 font-mono text-xs">
            <Link className="text-slate-500 hover:text-white transition-colors" href="/legal">
              LEGAL
            </Link>
            <Link className="text-slate-500 hover:text-white transition-colors" href="/privacy">
              PRIVACY
            </Link>
            <Link className="text-slate-500 hover:text-white transition-colors" href="/terms">
              TERMS
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
