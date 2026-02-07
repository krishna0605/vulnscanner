'use client';

import Link from 'next/link';

export default function LegalPage() {
  return (
    <>
      {/* Background Elements */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-mesh-gradient opacity-60"></div>

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
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative pt-32 pb-16 sm:pt-40 sm:pb-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass-panel rounded-[32px] p-8 md:p-12">
            <h1 className="text-4xl font-sans font-bold text-white mb-8">Legal Notice</h1>
            
            <div className="space-y-8 text-slate-300 leading-relaxed">
              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Disclaimer</h2>
                <p className="mb-4">
                  VulnScanner is a web application security scanning tool designed to help identify potential vulnerabilities in web applications. The information and services provided by VulnScanner are for educational and security assessment purposes only.
                </p>
                <p>
                  By using VulnScanner, you acknowledge that you have proper authorization to scan the target applications and that you will use our services responsibly and in compliance with all applicable laws and regulations.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Limitation of Liability</h2>
                <p className="mb-4">
                  VulnScanner and its creators shall not be held liable for any damages, losses, or legal consequences arising from the use or misuse of this service. Users are solely responsible for ensuring they have proper authorization before scanning any web application.
                </p>
                <p>
                  We do not guarantee the accuracy, completeness, or reliability of scan results. Security assessments should be performed by qualified professionals and our tool should be used as part of a comprehensive security strategy.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Intellectual Property</h2>
                <p>
                  All content, features, and functionality of VulnScanner, including but not limited to text, graphics, logos, and software, are the exclusive property of VulnScanner and are protected by international copyright, trademark, and other intellectual property laws.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Governing Law</h2>
                <p>
                  These terms shall be governed by and construed in accordance with applicable laws. Any disputes arising from the use of VulnScanner shall be resolved through appropriate legal channels.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Contact</h2>
                <p>
                  For any legal inquiries or concerns, please contact us through our official channels or visit{' '}
                  <a 
                    href="https://creative-engineer.dev/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-white hover:text-slate-300 underline transition-colors"
                  >
                    creative-engineer.dev
                  </a>.
                </p>
              </section>
            </div>

            <div className="mt-12 pt-8 border-t border-white/10">
              <Link 
                href="/" 
                className="inline-flex items-center text-slate-400 hover:text-white transition-colors font-mono text-sm"
              >
                <span className="material-symbols-outlined text-sm mr-2">arrow_back</span>
                Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
