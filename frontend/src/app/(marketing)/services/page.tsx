'use client';

import { useState } from 'react';
import Link from 'next/link';
import { services, Service } from '@/data/servicesData';
import ServiceModal from '@/components/services/ServiceModal';

export default function ServicesPage() {
  const [selectedService, setSelectedService] = useState<Service | null>(null);

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
                  className="text-white bg-white/10 px-4 py-2 rounded-full text-sm font-medium transition-all shadow-glow"
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

      <div className="relative pt-32 pb-16 overflow-hidden">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10 text-center">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-interactive-dark border border-white/10 text-white text-xs font-mono mb-6 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
            OPERATIONAL STATUS: ACTIVE
          </div>
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-sans font-bold tracking-tight mb-6 leading-tight text-white">
            Professional Security <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-500 text-glow">
              Services & Solutions
            </span>
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-slate-400 sm:text-xl font-light">
            Comprehensive cybersecurity strategies tailored for the modern enterprise. From
            proactive detection to rapid incident response.
          </p>
        </div>
      </div>

      <div className="py-12 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10 flex flex-col h-full">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">
                  travel_explore
                </span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Managed Detection & Response</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-6 flex-grow">
                24/7 autonomous monitoring of your entire digital estate. Our AI-driven SOC
                identifies and neutralizes threats before they impact operations.
              </p>
              <div className="pt-4 mt-auto border-t border-white/5">
                <button
                  onClick={() => setSelectedService(services[0])}
                  className="inline-flex items-center text-white text-xs font-mono font-bold uppercase tracking-wider hover:text-gray-300 transition-colors cursor-pointer"
                >
                  Learn more{' '}
                  <span className="material-symbols-outlined text-sm ml-2 group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10 flex flex-col h-full">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">fact_check</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Security Audits & Compliance</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-6 flex-grow">
                Rigorous assessment of your infrastructure against industry standards (SOC2, ISO
                27001, HIPAA). We provide the roadmap to certification.
              </p>
              <div className="pt-4 mt-auto border-t border-white/5">
                <button
                  onClick={() => setSelectedService(services[1])}
                  className="inline-flex items-center text-white text-xs font-mono font-bold uppercase tracking-wider hover:text-gray-300 transition-colors cursor-pointer"
                >
                  Learn more{' '}
                  <span className="material-symbols-outlined text-sm ml-2 group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10 flex flex-col h-full">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">emergency</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Incident Response</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-6 flex-grow">
                Immediate expert intervention during security breaches. We contain the threat,
                eradicate the adversary, and restore normal operations swiftly.
              </p>
              <div className="pt-4 mt-auto border-t border-white/5">
                <button
                  onClick={() => setSelectedService(services[2])}
                  className="inline-flex items-center text-white text-xs font-mono font-bold uppercase tracking-wider hover:text-gray-300 transition-colors cursor-pointer"
                >
                  Learn more{' '}
                  <span className="material-symbols-outlined text-sm ml-2 group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10 flex flex-col h-full">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">bug_report</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Penetration Testing</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-6 flex-grow">
                Ethical hacking simulations to expose vulnerabilities before malicious actors do.
                Comprehensive reporting for web, mobile, and network.
              </p>
              <div className="pt-4 mt-auto border-t border-white/5">
                <button
                  onClick={() => setSelectedService(services[3])}
                  className="inline-flex items-center text-white text-xs font-mono font-bold uppercase tracking-wider hover:text-gray-300 transition-colors cursor-pointer"
                >
                  Learn more{' '}
                  <span className="material-symbols-outlined text-sm ml-2 group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10 flex flex-col h-full">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">shield</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Cloud Security Architecture</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-6 flex-grow">
                Secure your AWS, Azure, or GCP environments. We design resilient architectures that
                scale with your business while minimizing attack surface.
              </p>
              <div className="pt-4 mt-auto border-t border-white/5">
                <button
                  onClick={() => setSelectedService(services[4])}
                  className="inline-flex items-center text-white text-xs font-mono font-bold uppercase tracking-wider hover:text-gray-300 transition-colors cursor-pointer"
                >
                  Learn more{' '}
                  <span className="material-symbols-outlined text-sm ml-2 group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>
              </div>
            </div>
            <div className="glass-panel p-8 rounded-[24px] hover:bg-section-dark transition-all duration-300 group border-t border-white/10 flex flex-col h-full">
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-glow">
                <span className="material-symbols-outlined text-white text-3xl">badge</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Virtual CISO (vCISO)</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-6 flex-grow">
                Executive-level security leadership on demand. Strategic planning, risk management,
                and board reporting without the full-time cost.
              </p>
              <div className="pt-4 mt-auto border-t border-white/5">
                <button
                  onClick={() => setSelectedService(services[5])}
                  className="inline-flex items-center text-white text-xs font-mono font-bold uppercase tracking-wider hover:text-gray-300 transition-colors cursor-pointer"
                >
                  Learn more{' '}
                  <span className="material-symbols-outlined text-sm ml-2 group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass-panel rounded-[32px] overflow-hidden border border-white/10 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-background-dark/80 to-transparent pointer-events-none"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2">
              <div className="p-10 lg:p-16 flex flex-col justify-center relative z-10">
                <div className="inline-flex items-center space-x-2 text-slate-400 font-mono text-sm mb-4">
                  <span className="w-8 h-[1px] bg-slate-400"></span>
                  <span>CONTACT US</span>
                </div>
                <h2 className="text-4xl font-bold text-white mb-6">
                  Schedule a Security Consultation
                </h2>
                <p className="text-slate-300 text-lg mb-8 font-light">
                  Unsure which solution fits your infrastructure? Speak directly with our lead
                  security engineers. We&apos;ll assess your current posture and propose a tailored
                  defense strategy.
                </p>
                <div className="space-y-4">
                  <div className="flex items-center text-slate-300">
                    <span className="material-symbols-outlined mr-4 text-white">mail</span>
                    <span>secure@vulnscanner.io</span>
                  </div>
                  <div className="flex items-center text-slate-300">
                    <span className="material-symbols-outlined mr-4 text-white">call</span>
                    <span>+1 (555) 019-2834</span>
                  </div>
                  <div className="flex items-center text-slate-300">
                    <span className="material-symbols-outlined mr-4 text-white">location_on</span>
                    <span>1288 Cyber Ln, Silicon Valley, CA</span>
                  </div>
                </div>
              </div>
              <div className="p-10 lg:p-16 bg-white/5 backdrop-blur-sm relative border-l border-white/5">
                <form className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label
                        className="block text-sm font-medium text-slate-300 mb-2"
                        htmlFor="first-name"
                      >
                        First Name
                      </label>
                      <input
                        className="form-input w-full rounded-lg px-4 py-3 focus:ring-1 focus:ring-white"
                        id="first-name"
                        placeholder="Jane"
                        type="text"
                      />
                    </div>
                    <div>
                      <label
                        className="block text-sm font-medium text-slate-300 mb-2"
                        htmlFor="last-name"
                      >
                        Last Name
                      </label>
                      <input
                        className="form-input w-full rounded-lg px-4 py-3 focus:ring-1 focus:ring-white"
                        id="last-name"
                        placeholder="Doe"
                        type="text"
                      />
                    </div>
                  </div>
                  <div>
                    <label
                      className="block text-sm font-medium text-slate-300 mb-2"
                      htmlFor="email"
                    >
                      Work Email
                    </label>
                    <input
                      className="form-input w-full rounded-lg px-4 py-3 focus:ring-1 focus:ring-white"
                      id="email"
                      placeholder="jane@company.com"
                      type="email"
                    />
                  </div>
                  <div>
                    <label
                      className="block text-sm font-medium text-slate-300 mb-2"
                      htmlFor="service"
                    >
                      Service of Interest
                    </label>
                    <select
                      className="form-input w-full rounded-lg px-4 py-3 focus:ring-1 focus:ring-white appearance-none cursor-pointer"
                      id="service"
                    >
                      <option className="bg-section-dark text-white">
                        Managed Detection & Response
                      </option>
                      <option className="bg-section-dark text-white">Security Audits</option>
                      <option className="bg-section-dark text-white">Penetration Testing</option>
                      <option className="bg-section-dark text-white">General Inquiry</option>
                    </select>
                  </div>
                  <div>
                    <label
                      className="block text-sm font-medium text-slate-300 mb-2"
                      htmlFor="message"
                    >
                      Message
                    </label>
                    <textarea
                      className="form-input w-full rounded-lg px-4 py-3 focus:ring-1 focus:ring-white"
                      id="message"
                      placeholder="Tell us about your security needs..."
                      rows={4}
                    ></textarea>
                  </div>
                  <button
                    className="w-full bg-white hover:bg-gray-200 text-black font-bold py-4 px-8 rounded-lg shadow-glow hover:shadow-glow-hover transition-all transform hover:-translate-y-1"
                    type="button"
                  >
                    Request Consultation
                  </button>
                </form>
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

      <ServiceModal
        service={selectedService}
        isOpen={!!selectedService}
        onClose={() => setSelectedService(null)}
      />
    </>
  );
}
