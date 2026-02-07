'use client';

import Link from 'next/link';
import MarketingFooter from '@/components/layout/MarketingFooter';

export default function PrivacyPage() {
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
            <h1 className="text-4xl font-sans font-bold text-white mb-8">Privacy Policy</h1>
            
            <div className="space-y-8 text-slate-300 leading-relaxed">
              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Information We Collect</h2>
                <p className="mb-4">
                  When you use VulnScanner, we may collect the following types of information:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Account information (email address, display name)</li>
                  <li>Scan targets and configurations you provide</li>
                  <li>Scan results and vulnerability reports</li>
                  <li>Usage data and analytics</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">How We Use Your Information</h2>
                <p className="mb-4">We use the collected information to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Provide and maintain our security scanning services</li>
                  <li>Generate vulnerability reports and analytics</li>
                  <li>Improve our scanning algorithms and service quality</li>
                  <li>Communicate with you about your account and scans</li>
                  <li>Ensure the security and integrity of our platform</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Data Security</h2>
                <p className="mb-4">
                  We implement industry-standard security measures to protect your data, including:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Encryption of data in transit and at rest</li>
                  <li>Secure authentication mechanisms</li>
                  <li>Regular security audits and monitoring</li>
                  <li>Access controls and authorization protocols</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Data Retention</h2>
                <p>
                  We retain your scan data and reports for as long as your account is active. You may request deletion of your data at any time through your account settings or by contacting us directly.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Third-Party Services</h2>
                <p>
                  VulnScanner may integrate with third-party services for authentication, analytics, or other functionality. These services have their own privacy policies, and we encourage you to review them.
                </p>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Your Rights</h2>
                <p className="mb-4">You have the right to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Access your personal data</li>
                  <li>Request correction of inaccurate data</li>
                  <li>Request deletion of your data</li>
                  <li>Export your data in a portable format</li>
                  <li>Opt-out of marketing communications</li>
                </ul>
              </section>

              <section>
                <h2 className="text-2xl font-bold text-white mb-4">Contact Us</h2>
                <p>
                  For privacy-related inquiries, please contact us through{' '}
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

      <MarketingFooter />
    </>
  );
}
