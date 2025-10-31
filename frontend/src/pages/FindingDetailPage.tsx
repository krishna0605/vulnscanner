import React from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

const mockFindingContent: Record<string, { title: string; severity: 'Critical' | 'High' | 'Medium' | 'Low'; cvss: number; cve?: string; cwe?: string; description: string; proof: string; discoveredAt: string; agent: string; assignee: string }> = {
  '500': {
    title: 'SQL Injection',
    severity: 'Critical',
    cvss: 9.8,
    cve: 'CVE-2023-12345',
    cwe: 'CWE-89',
    description:
      "A SQL Injection vulnerability was identified. This flaw allows an attacker to interfere with database queries. The instance was found in the 'productID' parameter on the search page.",
    proof:
      "GET /products?id=123' OR '1'='1 HTTP/1.1\nHost: vulnerable-website.com\nUser-Agent: Mozilla/5.0\nAccept: text/html,application/xhtml+xml\nConnection: close",
    discoveredAt: '2023-10-27 14:30 UTC',
    agent: 'Agent-US-East-1',
    assignee: 'Jane Doe',
  },
};

const FindingDetailPage: React.FC = () => {
  const navigate = useNavigate();
  const { scanId, findingId } = useParams();
  const data = mockFindingContent[String(findingId || '')] || mockFindingContent['500'];

  return (
    <div className="bg-[#0A0B14] text-white min-h-screen">
      <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/dashboard')}>
              <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAoGb6izEyw_X-IY8P4G1a15e7o30ltLXJVnqKuWW_bw3qlnzlNNTYrEnkZXhnNLOZHJAuVURDsIy0yKJ7KWbV5ulHg8NFsUL2QIoXSgs3tLTs46S3zXpP3WpI1co60H8nXr7VC9fJbj0cdMT5dL9n4F2bRQo20AdUqCu9h7m8G7YlLEnUZVXjv39K5ticnvVqwC6wCVyIQxyYAJcZ9UhO93dRoTmg_8WKC7IOoAhK-PraBlN-2I9Qr5IK5rlI__qB-QTLv_Fmr4eNx")' }} />
              <div className="flex flex-col"><h1 className="text-[#E0E0E0] text-base font-bold leading-normal">VulnScanner</h1></div>
            </div>
            <nav className="hidden md:flex items-center gap-4">
              <Link to="/dashboard" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-white"><span className="material-symbols-outlined text-base">dashboard</span>Dashboard</Link>
              <Link to="/projects" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#888888]"><span className="material-symbols-outlined text-base">folder</span>Projects</Link>
              <Link to="/scans" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#888888]"><span className="material-symbols-outlined text-base">radar</span>Scans</Link>
              <Link to="/reports" className="relative flex items-center gap-2 px-2 py-2 text-sm font-medium text-[#00FFFF]"><span className="material-symbols-outlined text-base">bar_chart</span>Reports</Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="relative z-10 flex h-auto w-full flex-col">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
          {/* Breadcrumbs */}
          <div className="flex flex-wrap items-center gap-2" aria-label="Breadcrumb">
            <Link to="/dashboard" className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Dashboard</Link>
            <span className="text-[#9da1b8] text-sm">/</span>
            <Link to="/reports" className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Reports</Link>
            {scanId && (
              <>
                <span className="text-[#9da1b8] text-sm">/</span>
                <Link to={`/reports/scan/${scanId}`} className="text-[#9da1b8] hover:text-[#00E5FF] text-sm">Scan #{scanId}</Link>
                <span className="text-[#9da1b8] text-sm">/</span>
              </>
            )}
            <span className="text-white text-sm">{data.title}</span>
          </div>

          {/* Header */}
          <div className="mt-4 flex flex-wrap justify-between gap-4">
            <div className="flex items-center gap-4">
              <p className="text-white text-4xl font-black leading-tight">{data.title}</p>
              <span
                className="inline-flex items-center rounded-full px-3 py-1 text-sm font-bold"
                style={{
                  backgroundColor: data.severity === 'Critical' ? 'rgba(255,59,48,0.1)' : data.severity === 'High' ? 'rgba(255,165,0,0.1)' : data.severity === 'Medium' ? 'rgba(255,215,0,0.1)' : 'rgba(0,120,255,0.1)',
                  color: data.severity === 'Critical' ? '#FF3B30' : data.severity === 'High' ? '#FFA500' : data.severity === 'Medium' ? '#FFD700' : '#007AFF',
                }}
                title={`Severity: ${data.severity}`}
              >
                {data.severity}
              </span>
            </div>
            <button className="flex min-w-[84px] items-center justify-center rounded-lg h-10 px-5 bg-[#3366FF] hover:bg-[#4D7FFF] transition-colors text-white text-sm font-bold" title="Mark this finding as resolved">
              <span className="material-symbols-outlined mr-2 text-base">task_alt</span>
              Mark as Resolved
            </button>
          </div>

          {/* Main layout */}
          <main className="grid grid-cols-12 gap-8">
            {/* Left nav & quick stats */}
            <aside className="col-span-12 lg:col-span-3">
              <div className="sticky top-8 flex flex-col gap-6">
                <nav className="flex flex-col gap-2 rounded-lg border border-[#3c3f53]/50 bg-[#0A0F1A]/50 p-4 backdrop-blur-sm" aria-label="Sections">
                  <a className="text-[#9da1b8] hover:text-white font-medium rounded-md px-3 py-2" href="#details">Details</a>
                  <a className="text-[#9da1b8] hover:text-white font-medium rounded-md px-3 py-2" href="#evidence">Evidence</a>
                  <a className="text-white bg-[#00E5FF]/10 font-medium rounded-md px-3 py-2" href="#recommendation">Recommendation</a>
                </nav>
                <div className="rounded-lg border border-[#3c3f53]/50 bg-[#0A0F1A]/50 p-4 backdrop-blur-sm">
                  <h3 className="text-white text-lg font-bold mb-4">Quick Stats</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between"><span className="text-[#9da1b8]">CVSS Score</span><span className="font-bold" style={{ color: '#FF3B30' }}>{data.cvss}</span></div>
                    <div className="flex justify-between"><span className="text-[#9da1b8]">CVE</span><span className="font-mono text-[#00E5FF]">{data.cve}</span></div>
                    <div className="flex justify-between"><span className="text-[#9da1b8]">CWE</span><span className="font-mono text-[#00E5FF]">{data.cwe}</span></div>
                  </div>
                </div>
              </div>
            </aside>

            {/* Center column */}
            <div className="col-span-12 lg:col-span-6 flex flex-col gap-8">
              <section id="details" className="flex flex-col gap-4">
                <h3 className="text-white text-lg font-bold">Details</h3>
                <details className="flex flex-col rounded-lg border border-[#3c3f53]/50 bg-[#111218]/80 px-[15px] py-[7px]" open>
                  <summary className="flex cursor-pointer items-center justify-between gap-6 py-2">
                    <p className="text-white text-sm font-medium">Vulnerability Description</p>
                    <div className="text-white"><span className="material-symbols-outlined text-xl">expand_more</span></div>
                  </summary>
                  <p className="text-[#9da1b8] text-sm leading-relaxed pb-2">{data.description}</p>
                </details>
              </section>
              <section id="evidence" className="flex flex-col gap-4">
                <h3 className="text-white text-lg font-bold">Evidence</h3>
                <div className="rounded-lg border border-[#3c3f53]/50 bg-[#111218]/80 overflow-hidden">
                  <div className="flex border-b border-[#3c3f53]/50 gap-6 px-4">
                    <button className="flex flex-col items-center justify-center border-b-[3px] border-b-[#00E5FF] text-white py-3">
                      <p className="text-sm font-bold">HTTP Request</p>
                    </button>
                    <button className="flex flex-col items-center justify-center border-b-[3px] border-b-transparent text-[#9da1b8] hover:text-white py-3">
                      <p className="text-sm font-bold">HTTP Response</p>
                    </button>
                  </div>
                  <div className="p-4 bg-black/30 font-mono text-sm leading-relaxed overflow-x-auto">
                    <pre><code>{data.proof}</code></pre>
                  </div>
                </div>
                <div className="rounded-lg border border-[#3c3f53]/50 bg-[#111218]/80 p-4">
                  <p className="text-white text-sm font-medium mb-2">Proof of Concept</p>
                  <p className="text-[#9da1b8] text-sm leading-relaxed">
                    The payload <code className="bg-[#00E5FF]/10 text-[#00E5FF] px-1 py-0.5 rounded">' OR '1'='1</code> was injected into the <code className="bg-gray-700 text-gray-300 px-1 py-0.5 rounded">id</code> parameter, returning all records and confirming the vulnerability.
                  </p>
                </div>
              </section>
            </div>

            {/* Right column */}
            <aside className="col-span-12 lg:col-span-3">
              <div className="sticky top-8 flex flex-col gap-6">
                <section id="recommendation" className="rounded-lg border border-[#3c3f53]/50 bg-[#0A0F1A]/50 p-4 backdrop-blur-sm">
                  <h3 className="text-white text-lg font-bold mb-4">Remediation Steps</h3>
                  <ol className="list-decimal list-inside space-y-3 text-[#9da1b8] text-sm">
                    <li>Use parameterized queries (prepared statements).</li>
                    <li>Validate user input for format and type.</li>
                    <li>Restrict database permissions (least privilege).</li>
                  </ol>
                </section>
                <div className="rounded-lg border border-[#3c3f53]/50 bg-[#0A0F1A]/50 p-4 backdrop-blur-sm">
                  <h3 className="text-white text-lg font-bold mb-4">References</h3>
                  <ul className="space-y-2">
                    <li><a className="flex items-center gap-2 text-[#00E5FF] hover:underline text-sm" href="https://owasp.org/www-community/attacks/SQL_Injection" target="_blank" rel="noopener noreferrer"><span className="material-symbols-outlined text-base">link</span>OWASP: SQL Injection</a></li>
                    <li><a className="flex items-center gap-2 text-[#00E5FF] hover:underline text-sm" href="https://cwe.mitre.org/data/definitions/89.html" target="_blank" rel="noopener noreferrer"><span className="material-symbols-outlined text-base">link</span>CWE-89: Improper Neutralization</a></li>
                  </ul>
                </div>
                <div className="rounded-lg border border-[#3c3f53]/50 bg-[#0A0F1A]/50 p-4 backdrop-blur-sm">
                  <h3 className="text-white text-lg font-bold mb-4">Finding Details</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between"><span className="text-[#9da1b8]">Discovered On</span><span className="font-medium text-white">{data.discoveredAt}</span></div>
                    <div className="flex justify-between"><span className="text-[#9da1b8]">Scanner Agent</span><span className="font-medium text-white">{data.agent}</span></div>
                    <div className="flex justify-between"><span className="text-[#9da1b8]">Assigned To</span><span className="font-medium text-white">{data.assignee}</span></div>
                  </div>
                </div>
              </div>
            </aside>
          </main>
        </div>
      </div>
    </div>
  );
};

export default FindingDetailPage;