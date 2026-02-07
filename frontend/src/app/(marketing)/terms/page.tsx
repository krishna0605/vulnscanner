'use client';

import Link from 'next/link';

export default function TermsPage() {
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
            <h1 className="text-4xl font-sans font-bold text-white mb-8">Terms of Service</h1>
            
            <div className="space-y-8 text-slate-300 leading-relaxed">
              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Acceptance of Terms</h2>
                <p>
                  By accessing and using VulnScanner, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our services.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Authorized Use</h2>
                <p className="mb-4">
                  You agree to use VulnScanner only for lawful purposes and only on systems for which you have explicit authorization to perform security testing. You must:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Have proper written authorization before scanning any target</li>
                  <li>Only scan systems you own or have explicit permission to test</li>
                  <li>Not use our service to attack, disrupt, or harm any systems</li>
                  <li>Comply with all applicable local, state, and international laws</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Prohibited Activities</h2>
                <p className="mb-4">You may not use VulnScanner to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Scan systems without proper authorization</li>
                  <li>Attempt to exploit vulnerabilities on systems you do not own</li>
                  <li>Conduct denial-of-service attacks</li>
                  <li>Access or attempt to access data belonging to others</li>
                  <li>Violate any applicable laws or regulations</li>
                  <li>Reverse engineer or attempt to extract our scanning algorithms</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Account Responsibilities</h2>
                <p>
                  You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You agree to notify us immediately of any unauthorized use of your account.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Service Availability</h2>
                <p>
                  We strive to maintain high availability of our services but do not guarantee uninterrupted access. We reserve the right to modify, suspend, or discontinue any part of our service at any time.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Limitation of Liability</h2>
                <p>
                  VulnScanner is provided "as is" without warranties of any kind. We shall not be liable for any direct, indirect, incidental, or consequential damages arising from your use of our services. You assume full responsibility for the use of our scanning tools.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Termination</h2>
                <p>
                  We reserve the right to terminate or suspend your account at any time for violation of these terms or for any other reason at our sole discretion.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Changes to Terms</h2>
                <p>
                  We may update these Terms of Service from time to time. Continued use of VulnScanner after changes are posted constitutes acceptance of the modified terms.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Contact</h2>
                <p>
                  For questions about these Terms of Service, please contact us through{' '}
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

              <section className="text-sm text-slate-500">
                <p>Last updated: February 2026</p>
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
