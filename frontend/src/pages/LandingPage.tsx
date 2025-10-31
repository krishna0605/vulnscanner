import React, { useState } from 'react';
import { Link } from 'react-router-dom';

// Defer YouTube embed until user interaction to avoid aborted loads in dev
const VideoEmbed: React.FC = () => {
  const [loaded, setLoaded] = useState(false);
  const videoSrc = "https://www.youtube-nocookie.com/embed/4YOpILi9Oxs?rel=0&modestbranding=1";

  return (
    <div className="relative w-full" style={{ paddingTop: '56.25%' }}>
      {loaded ? (
        <iframe
          title="VulnScanner Demo"
          src={videoSrc}
          className="absolute top-0 left-0 w-full h-full rounded-lg"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
        />
      ) : (
        <button
          type="button"
          className="absolute top-0 left-0 w-full h-full rounded-lg flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors"
          onClick={() => setLoaded(true)}
          aria-label="Load video"
        >
          <span className="material-symbols-outlined text-white text-5xl">play_circle</span>
        </button>
      )}
    </div>
  );
};

const LandingPage: React.FC = () => {
  return (
    <div className="relative w-full overflow-x-hidden bg-[#0B0D12] text-[#A0A0B0] font-sans">
      <div className="absolute inset-0 animated-bg" />

      <div className="relative z-10 flex min-h-screen flex-col grid-overlay">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 mx-auto max-w-7xl">
          <div className="flex items-center gap-3 text-[#F0F0F0]">
            <div className="text-[#0ea5e9]">
              <svg className="h-8 w-8" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path fill="currentColor" fillRule="evenodd" d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z" />
              </svg>
            </div>
            <h2 className="text-[#F0F0F0] text-xl font-bold tracking-[-0.015em]">VulnScanner</h2>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm ml-6">
            <a href="#features" className="link-subtle text-[#C8C8D6]">Features</a>
            <a href="#services" className="link-subtle text-[#C8C8D6]">Services</a>
            <Link to="/pricing" className="link-subtle text-[#C8C8D6]">Pricing</Link>
            <a href="#learn" className="link-subtle text-[#C8C8D6]">Learn</a>
            <a href="#contact" className="link-subtle text-[#C8C8D6]">Contact</a>
          </nav>
          <div className="flex gap-3 ml-6 md:ml-8">
            <Link to="/login" className="btn-trail cursor-pointer flex items-center justify-center rounded-lg h-10 px-4 bg-[rgba(14,165,233,0.2)] text-[#0ea5e9] text-sm font-bold hover:bg-[rgba(14,165,233,0.3)]">Login</Link>
            <Link to="/register" className="btn-trail cursor-pointer flex items-center justify-center rounded-lg h-10 px-5 bg-[#0ea5e9] text-[#0B0D12] text-sm font-bold glow-on-hover">Sign Up</Link>
          </div>
        </header>

        {/* Hero */}
        <main className="flex-grow">
          <section className="py-16 sm:py-24">
            <div className="flex min-h-[420px] flex-col gap-6 text-center items-center justify-center px-6 max-w-7xl mx-auto">
              <div className="flex flex-col gap-4 max-w-3xl fade-in-up">
                <h1 className="text-[#F0F0F0] text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight">Illuminate Your Web Security.</h1>
                <p className="text-base sm:text-lg text-[#A0A0B0] max-w-2xl mx-auto">Next‑generation vulnerability scanner for developers and security teams. Find, manage, and fix security flaws with speed and precision.</p>
              </div>
              <div className="flex gap-4">
                <Link to="/login" className="btn-trail cursor-pointer flex items-center justify-center rounded-lg h-12 px-6 bg-[rgba(14,165,233,0.2)] text-[#0ea5e9] text-base font-bold hover:bg-[rgba(14,165,233,0.3)]">Get Started</Link>
                <a href="#services" className="btn-trail cursor-pointer flex items-center justify-center rounded-lg h-12 px-6 bg-[rgba(14,165,233,0.2)] text-[#0ea5e9] text-base font-bold hover:bg-[rgba(14,165,233,0.3)]">Explore Services</a>
              </div>
              <div className="mt-4 flex items-center gap-6 text-[#8C8CA0] text-xs">
                <span className="float-slow">OWASP Coverage</span>
                <span className="float-slow" style={{animationDelay:'0.8s'}}>Actionable Insights</span>
                <span className="float-slow" style={{animationDelay:'1.6s'}}>CI/CD Friendly</span>
              </div>
            </div>
          </section>

          {/* Features */}
          <section id="features" className="px-6 py-16 max-w-7xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-[#F0F0F0] text-3xl font-bold tracking-tight">Why VulnScanner?</h2>
              <p className="text-[#A0A0B0] text-sm sm:text-base max-w-2xl mx-auto">Discover powerful features that make our scanner the top choice for modern security teams.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <div className="text-[#0ea5e9] mb-2">
                  <svg className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l7 4v5c0 5-3.5 9.74-7 11-3.5-1.26-7-6-7-11V6l7-4z"></path></svg>
                </div>
                <h3 className="text-[#F0F0F0] text-lg font-bold mt-2">Comprehensive Scanning</h3>
                <p className="text-[#A0A0B0] text-sm">Covers OWASP Top 10, misconfigurations, and common vulnerabilities.</p>
              </div>
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <div className="text-[#0ea5e9] mb-2">
                  <svg className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm4 0h2V7H7v6zm4 0h2V3h-2v10zm4 0h2V9h-2v4zm4 0h2V5h-2v8z"></path></svg>
                </div>
                <h3 className="text-[#F0F0F0] text-lg font-bold mt-2">Actionable Reporting</h3>
                <p className="text-[#A0A0B0] text-sm">Clear, prioritized reports to resolve issues quickly and confidently.</p>
              </div>
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <div className="text-[#0ea5e9] mb-2">
                  <svg className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor"><path d="M7 12l5 5 5-5-1.41-1.41L13 13.17V4h-2v9.17l-2.59-2.58L7 12z"></path></svg>
                </div>
                <h3 className="text-[#F0F0F0] text-lg font-bold mt-2">Seamless Integration</h3>
                <p className="text-[#A0A0B0] text-sm">Integrates with CI/CD and popular developer tools with ease.</p>
              </div>
            </div>
          </section>

          {/* Cybersecurity Video */}
          <section id="cyber-video" className="px-6 py-16 max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
              {/* Left: Heading, description, video */}
              <div className="space-y-4">
                <h2 className="text-[#F0F0F0] text-3xl font-bold tracking-tight">See VulnScanner in Action</h2>
                <p className="text-[#A0A0B0] text-sm sm:text-base max-w-2xl">Watch our comprehensive demonstration of the Enhanced Vulnerability Scanner. This video showcases the key features, scanning capabilities, and how our platform helps security teams identify and remediate vulnerabilities efficiently.</p>
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 backdrop-blur-sm">
                  <VideoEmbed />
                </div>
                <p className="text-xs text-[#8C8CA0]">Watch the complete VulnScanner demonstration to see how our platform streamlines vulnerability management.</p>
                {/* Structured data for SEO */}
                <script type="application/ld+json">
                  {JSON.stringify({
                    '@context': 'https://schema.org',
                    '@type': 'VideoObject',
                    name: 'VulnScanner Demo',
                    description: 'Enhanced vulnerability scanner demonstration and overview.',
                    thumbnailUrl: ['https://i.ytimg.com/vi/4YOpILi9Oxs/hqdefault.jpg'],
                    uploadDate: '2024-01-01',
                    publisher: { '@type': 'Organization', name: 'VulnScanner' },
                    contentUrl: 'https://www.youtube-nocookie.com/embed/4YOpILi9Oxs',
                    embedUrl: 'https://www.youtube-nocookie.com/embed/4YOpILi9Oxs'
                  })}
                </script>
              </div>

              {/* Right: Concepts, resources, CTA */}
              <div className="space-y-6">
                <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                  <h3 className="text-[#F0F0F0] font-semibold mb-3">Key Concepts</h3>
                  <ul className="space-y-2 text-[#A0A0B0] text-sm">
                    <li><span className="font-medium text-[#F0F0F0]">CIA Triad:</span> confidentiality, integrity, availability.</li>
                    <li><span className="font-medium text-[#F0F0F0]">Authentication & MFA:</span> verify identities with multiple factors.</li>
                    <li><span className="font-medium text-[#F0F0F0]">Encryption:</span> protect data in transit and at rest.</li>
                    <li><span className="font-medium text-[#F0F0F0]">Secure Coding:</span> validate input, sanitize output, use parameterized queries.</li>
                    <li><span className="font-medium text-[#F0F0F0]">Threat Modeling:</span> map assets, adversaries, and mitigations.</li>
                  </ul>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-6">
                  <h3 className="text-[#F0F0F0] font-semibold mb-3">Educational Resources</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <a href="https://owasp.org/Top10/" target="_blank" rel="noopener noreferrer" className="feature-card rounded-lg border border-white/10 bg-black/30 p-4 hover:border-[#0ea5e9]/50 transition-colors">
                      <span className="text-[#F0F0F0] font-semibold">OWASP Top 10</span>
                      <p className="text-[#A0A0B0] text-sm">Most critical web app risks.</p>
                    </a>
                    <a href="https://www.nist.gov/cyberframework" target="_blank" rel="noopener noreferrer" className="feature-card rounded-lg border border-white/10 bg-black/30 p-4 hover:border-[#0ea5e9]/50 transition-colors">
                      <span className="text-[#F0F0F0] font-semibold">NIST CSF</span>
                      <p className="text-[#A0A0B0] text-sm">Framework to manage cyber risk.</p>
                    </a>
                    <a href="https://attack.mitre.org/" target="_blank" rel="noopener noreferrer" className="feature-card rounded-lg border border-white/10 bg-black/30 p-4 hover:border-[#0ea5e9]/50 transition-colors">
                      <span className="text-[#F0F0F0] font-semibold">MITRE ATT&CK</span>
                      <p className="text-[#A0A0B0] text-sm">Adversary tactics and techniques.</p>
                    </a>
                    <a href="https://www.cisa.gov/topics/cybersecurity-best-practices" target="_blank" rel="noopener noreferrer" className="feature-card rounded-lg border border-white/10 bg-black/30 p-4 hover:border-[#0ea5e9]/50 transition-colors">
                      <span className="text-[#F0F0F0] font-semibold">CISA Best Practices</span>
                      <p className="text-[#A0A0B0] text-sm">Guidance from the US cyber agency.</p>
                    </a>
                  </div>
                </div>
                <div className="flex flex-wrap gap-3">
                  <a href="#learn" className="btn-trail flex items-center justify-center rounded-lg h-10 px-4 bg-[rgba(14,165,233,0.2)] text-[#0ea5e9] text-sm font-bold hover:bg-[rgba(14,165,233,0.3)]">Explore More Basics</a>
                  <a href="https://cheatsheetseries.owasp.org/" target="_blank" rel="noopener noreferrer" className="btn-trail glow-on-hover flex items-center justify-center rounded-lg h-10 px-5 bg-[#0ea5e9] text-[#0B0D12] text-sm font-bold">Dive Deeper</a>
                </div>
              </div>
            </div>
          </section>

          {/* Services */}
          <section id="services" className="px-6 py-16 max-w-7xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-[#F0F0F0] text-3xl font-bold tracking-tight">Our Services</h2>
              <p className="text-[#A0A0B0] text-sm sm:text-base max-w-3xl mx-auto">From automated scans to guided remediation, we help teams build and maintain secure applications throughout the development lifecycle.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-[#F0F0F0] font-semibold mb-1">Automated Vulnerability Scans</h3>
                <p className="text-[#A0A0B0] text-sm">Schedule scans or trigger them on demand to catch issues early.</p>
              </div>
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-[#F0F0F0] font-semibold mb-1">Real-Time Monitoring</h3>
                <p className="text-[#A0A0B0] text-sm">Continuous monitoring for new threats and misconfigurations.</p>
              </div>
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-[#F0F0F0] font-semibold mb-1">Detailed Reports & Analytics</h3>
                <p className="text-[#A0A0B0] text-sm">Visual summaries and drill-down details for effective triage.</p>
              </div>
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-[#F0F0F0] font-semibold mb-1">Integration Ecosystem</h3>
                <p className="text-[#A0A0B0] text-sm">Connect with GitHub, GitLab, Jira, Slack, and your CI pipeline.</p>
              </div>
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-[#F0F0F0] font-semibold mb-1">Compliance Assistance</h3>
                <p className="text-[#A0A0B0] text-sm">Support for standards like OWASP, ISO 27001, SOC 2, and more.</p>
              </div>
              <div className="feature-card rounded-xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-[#F0F0F0] font-semibold mb-1">Guided Remediation</h3>
                <p className="text-[#A0A0B0] text-sm">Step-by-step fixes with context-aware recommendations.</p>
              </div>
            </div>
          </section>

          {/* Learn */}
          <section id="learn" className="px-6 py-16 max-w-7xl mx-auto">
            <div className="text-center mb-10">
              <h2 className="text-[#F0F0F0] text-3xl font-bold tracking-tight">Cybersecurity Basics & Precautions</h2>
              <p className="text-[#A0A0B0] text-sm sm:text-base max-w-3xl mx-auto">Build a security-first culture. Here are essentials and practical steps to reduce risk.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <h3 className="text-[#F0F0F0] font-semibold mb-3">Core Principles</h3>
                <ul className="space-y-2 text-[#A0A0B0] text-sm">
                  <li>Least privilege: give only necessary access.</li>
                  <li>Secure coding: validate inputs, escape outputs.</li>
                  <li>Patch management: update dependencies regularly.</li>
                  <li>Authentication: MFA and strong password policies.</li>
                  <li>Threat modeling: identify assets, threats, and mitigations.</li>
                </ul>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <h3 className="text-[#F0F0F0] font-semibold mb-3">Precautions</h3>
                <ul className="space-y-2 text-[#A0A0B0] text-sm">
                  <li>Phishing awareness: verify sender and links.</li>
                  <li>Secrets hygiene: never commit credentials to VCS.</li>
                  <li>Backups: maintain and test restore procedures.</li>
                  <li>Logging & monitoring: detect anomalies early.</li>
                  <li>Secure configs: close unused ports, enforce TLS.</li>
                </ul>
              </div>
            </div>
          </section>

          {/* CTA */}
          <section className="px-6 py-16 text-center max-w-7xl mx-auto">
            <h3 className="text-[#F0F0F0] text-2xl font-bold mb-3">Ready to elevate your security posture?</h3>
            <p className="text-[#A0A0B0] max-w-2xl mx-auto mb-6">Start with a free scan and see actionable insights within minutes.</p>
            <div className="flex justify-center gap-4">
              <Link to="/login" className="btn-trail glow-on-hover flex items-center justify-center rounded-lg h-12 px-6 bg-[#0ea5e9] text-[#0B0D12] text-base font-bold">Start Free</Link>
              <Link to="/register" className="flex items-center justify-center rounded-lg h-12 px-6 bg-[rgba(14,165,233,0.2)] text-[#0ea5e9] text-base font-bold hover:bg-[rgba(14,165,233,0.3)]">Create Account</Link>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer id="contact" className="pt-10 pb-12 border-t border-white/10 px-6 max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <h4 className="text-[#F0F0F0] font-semibold mb-2">Product</h4>
              <ul className="text-sm text-[#A0A0B0] space-y-1">
                <li><a href="#features" className="link-subtle">Features</a></li>
                <li><a href="#services" className="link-subtle">Services</a></li>
                <li><Link to="/login" className="link-subtle">Get Started</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-[#F0F0F0] font-semibold mb-2">Resources</h4>
              <ul className="text-sm text-[#A0A0B0] space-y-1">
                <li><a href="#learn" className="link-subtle">Learning Center</a></li>
                <li><a href="#learn" className="link-subtle">Best Practices</a></li>
                <li><a href="#learn" className="link-subtle">OWASP Overview</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-[#F0F0F0] font-semibold mb-2">Company</h4>
              <ul className="text-sm text-[#A0A0B0] space-y-1">
                <li><a href="#contact" className="link-subtle">Contact</a></li>
                <li><a href="#contact" className="link-subtle">Support</a></li>
                <li><a href="#contact" className="link-subtle">Status</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-[#F0F0F0] font-semibold mb-2">Legal</h4>
              <ul className="text-sm text-[#A0A0B0] space-y-1">
                <li><a href="#features" className="link-subtle">Privacy Policy</a></li>
                <li><a href="#services" className="link-subtle">Terms of Service</a></li>
                <li><a href="#learn" className="link-subtle">Security</a></li>
              </ul>
            </div>
          </div>
          <p className="mt-8 text-[#8C8CA0] text-xs">© 2024 VulnScanner. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;