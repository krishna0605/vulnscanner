import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

interface ScanConfiguration {
  max_depth: number;
  max_pages: number;
  requests_per_second: number;
  timeout: number;
  follow_redirects: boolean;
  respect_robots: boolean;
  user_agent: string;
  scope_patterns: string[];
  exclude_patterns: string[];
  authentication?: any;
}

interface Project {
  id: number;
  name: string;
  target_domain: string;
  description?: string;
}

const ScanConfigPage: React.FC = () => {
  const navigate = useNavigate();
  const [targetUrl, setTargetUrl] = useState('');
  const [scanDepth, setScanDepth] = useState(50);
  const [rateLimit, setRateLimit] = useState(10);
  const [followRedirects, setFollowRedirects] = useState(true);
  const [useAuth, setUseAuth] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  const getAuthHeaders = () => {
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const loadProjects = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/projects`, {
        headers: getAuthHeaders()
      });
      setProjects(response.data);
      if (response.data.length > 0) {
        setSelectedProject(response.data[0].id);
        setTargetUrl(response.data[0].target_domain);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
      setError('Failed to load projects. Please try again.');
    }
  }, [API_BASE_URL]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleProjectChange = (projectId: number) => {
    setSelectedProject(projectId);
    const project = projects.find(p => p.id === projectId);
    if (project) {
      setTargetUrl(project.target_domain);
    }
  };

  const handleStartScan = async () => {
    if (!selectedProject) {
      setError('Please select a project to scan.');
      return;
    }

    if (!targetUrl.trim()) {
      setError('Please enter a target URL.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const configuration: ScanConfiguration = {
        max_depth: Math.round((scanDepth / 100) * 10), // Convert 0-100 to 1-10
        max_pages: 1000,
        requests_per_second: rateLimit,
        timeout: 30,
        follow_redirects: followRedirects,
        respect_robots: true,
        user_agent: "Enhanced-Vulnerability-Scanner/1.0",
        scope_patterns: [targetUrl],
        exclude_patterns: []
      };

      if (useAuth) {
        configuration.authentication = {
          type: 'basic',
          credentials: {}
        };
      }

      const response = await axios.post(
        `${API_BASE_URL}/projects/${selectedProject}/scans`,
        { configuration },
        { headers: getAuthHeaders() }
      );

      console.log('Scan created successfully:', response.data);
      
      // Navigate to dashboard with success message
      navigate('/dashboard', { 
        state: { 
          message: 'Scan started successfully!',
          scanId: response.data.id 
        }
      });

    } catch (error: any) {
      console.error('Failed to start scan:', error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Failed to start scan. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full">
      {/* Background */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-transparent bg-[radial-gradient(#1A1A2E_1px,transparent_1px)] [background-size:32px_32px]" />
      <div className="absolute top-0 left-0 -z-10 h-1/2 w-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(74,144,226,0.14),rgba(255,255,255,0))]" />

      {/* Top navbar */}
      <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
        <div className="flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-3 cursor-pointer">
            <div
              className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9"
              style={{
                backgroundImage:
                  'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAoGb6izEyw_X-IY8P4G1a15e7o30ltLXJVnqKuWW_bw3qlnzlNNTYrEnkZXhnNLOZHJAuVURDsIy0yKJ7KWbV5ulHg8NFsUL2QIoXSgs3tLTs46S3zXpP3WpI1co60H8nXr7VC9fJbj0cdMT5dL9n4F2bRQo20AdUqCu9h7m8G7YlLEnUZVXjv39K5ticnvVqwC6wCVyIQxyYAJcZ9UhO93dRoTmg_8WKC7IOoAhK-PraBlN-2I9Qr5IK5rlI__qB-QTLv_Fmr4eNx")',
              }}
            />
            <div className="flex flex-col">
              <h1 className="text-[#E0E0E0] text-base font-bold leading-normal">VulnScanner</h1>
            </div>
          </Link>
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="text-[#888888] hover:text-white text-sm font-medium">Dashboard</Link>
            <Link to="/profile" className="text-[#888888] hover:text-white text-sm font-medium">Profile</Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-4xl">
          <div className="flex flex-wrap justify-between gap-3 mb-8">
            <div className="flex flex-col gap-2">
              <h1 className="text-4xl font-bold tracking-tight">Configure Scan</h1>
              <p className="text-[#888888] text-base">Set up the parameters for your new web vulnerability scan.</p>
            </div>
          </div>

          <div className="flex flex-col gap-10">
            {/* Error Message */}
            {error && (
              <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
                {error}
              </div>
            )}

            {/* Project Selection */}
            <section>
              <label className="flex flex-col w-full">
                <p className="text-base font-medium pb-2">Select Project</p>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#888888]">folder</span>
                  <select 
                    value={selectedProject || ''} 
                    onChange={(e) => handleProjectChange(Number(e.target.value))}
                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#E0E0E0] focus:outline-0 focus:ring-2 focus:ring-[#4A90E2]/50 border border-[#2E2E3F] bg-[#131523] focus:border-[#4A90E2]/50 h-14 pl-12 pr-4 text-base"
                  >
                    <option value="">Select a project...</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id} className="bg-[#131523] text-[#E0E0E0]">
                        {project.name} - {project.target_domain}
                      </option>
                    ))}
                  </select>
                </div>
              </label>
            </section>

            {/* Target URL */}
            <section>
              <label className="flex flex-col w-full">
                <p className="text-base font-medium pb-2">Target URL</p>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#888888]">link</span>
                  <input 
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#E0E0E0] focus:outline-0 focus:ring-2 focus:ring-[#4A90E2]/50 border border-[#2E2E3F] bg-[#131523] focus:border-[#4A90E2]/50 h-14 placeholder:text-[#888888] pl-12 pr-4 text-base" 
                    placeholder="Enter target URL or IP address (e.g., https://example.com)" 
                  />
                </div>
              </label>
            </section>

            {/* Scan Policy */}
            <section className="flex flex-col gap-6 p-6 rounded-xl border border-[#2E2E3F] bg-[#131523]/80">
              <h2 className="text-xl font-bold">Scan Policy</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Scan Depth */}
                <div className="flex flex-col gap-3">
                  <label className="font-medium" htmlFor="scan-depth">
                    Scan Depth: {Math.round((scanDepth / 100) * 10)} levels
                  </label>
                  <input 
                    id="scan-depth" 
                    type="range" 
                    min={0} 
                    max={100} 
                    value={scanDepth}
                    onChange={(e) => setScanDepth(Number(e.target.value))}
                    className="w-full h-2 bg-[#2E2E3F] rounded-lg appearance-none cursor-pointer accent-[#4A90E2]" 
                  />
                  <div className="flex justify-between text-sm text-[#888888]"><span>Surface</span><span>Full</span></div>
                </div>
                {/* Rate Limit */}
                <div className="flex flex-col gap-3">
                  <label className="font-medium" htmlFor="rate-limit">
                    Rate Limit: {rateLimit} requests/sec
                  </label>
                  <input 
                    id="rate-limit" 
                    type="range" 
                    min={1} 
                    max={50} 
                    value={rateLimit}
                    onChange={(e) => setRateLimit(Number(e.target.value))}
                    className="w-full h-2 bg-[#2E2E3F] rounded-lg appearance-none cursor-pointer accent-[#4A90E2]" 
                  />
                  <div className="flex justify-between text-sm text-[#888888]"><span>1</span><span>50</span></div>
                </div>
              </div>
            </section>

            {/* Scheduling */}
            <section className="p-6 rounded-xl border border-[#2E2E3F] bg-[#131523]/80">
              <h2 className="text-xl font-bold mb-4">Scheduling</h2>
              <div className="flex">
                <div className="flex h-10 w-full max-w-sm items-center justify-center rounded-lg bg-[#0A0B14] p-1 border border-[#2E2E3F]">
                  <label className="flex cursor-pointer h-full grow items-center justify-center overflow-hidden rounded-md px-2 has-[:checked]:bg-[#4A90E2]/20 has-[:checked]:text-[#4A90E2] text-[#888888] text-sm font-medium transition-colors">
                    <span className="truncate">One-Time</span>
                    <input defaultChecked className="invisible absolute w-0" name="scan-schedule" type="radio" value="One-Time" />
                  </label>
                  <label className="flex cursor-pointer h-full grow items-center justify-center overflow-hidden rounded-md px-2 has-[:checked]:bg-[#4A90E2]/20 has-[:checked]:text-[#4A90E2] text-[#888888] text-sm font-medium transition-colors">
                    <span className="truncate">Recurring</span>
                    <input className="invisible absolute w-0" name="scan-schedule" type="radio" value="Recurring" />
                  </label>
                </div>
              </div>
            </section>

            {/* Advanced Options */}
            <section>
              <details className="group">
                <summary className="list-none flex cursor-pointer items-center justify-between p-4 rounded-lg hover:bg-[#131523] transition-colors">
                  <h2 className="text-xl font-bold">Advanced Options</h2>
                  <span className="material-symbols-outlined text-[#888888] transition-transform group-open:rotate-180">expand_more</span>
                </summary>
                <div className="mt-4 flex flex-col gap-6 p-6 rounded-xl border border-[#2E2E3F] bg-[#131523]/80">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                    {/* Toggles */}
                    <div className="flex flex-col gap-4">
                      <label className="flex items-center justify-between cursor-pointer">
                        <span className="font-medium">Follow Redirects</span>
                        <input 
                          checked={followRedirects}
                          onChange={(e) => setFollowRedirects(e.target.checked)}
                          className="sr-only peer" 
                          type="checkbox" 
                        />
                        <div className="relative w-11 h-6 bg-[#2E2E3F] rounded-full peer peer-focus:ring-2 peer-focus:ring-[#4A90E2]/50 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:start-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#4A90E2]"></div>
                      </label>
                      <label className="flex items-center justify-between cursor-pointer">
                        <span className="font-medium">Use Authentication</span>
                        <input 
                          checked={useAuth}
                          onChange={(e) => setUseAuth(e.target.checked)}
                          className="sr-only peer" 
                          type="checkbox" 
                        />
                        <div className="relative w-11 h-6 bg-[#2E2E3F] rounded-full peer peer-focus:ring-2 peer-focus:ring-[#4A90E2]/50 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:start-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#4A90E2]"></div>
                      </label>
                    </div>
                    {/* Custom Headers */}
                    <div className="flex flex-col gap-3">
                      <p className="font-medium">Custom Headers</p>
                      <div className="flex gap-2">
                        <input className="form-input flex-1 rounded-lg text-[#E0E0E0] focus:outline-0 focus:ring-2 focus:ring-[#4A90E2]/50 border border-[#2E2E3F] bg-[#0A0B14] focus:border-[#4A90E2]/50 h-10 placeholder:text-[#888888] px-3 text-sm" placeholder="Header Name" />
                        <input className="form-input flex-1 rounded-lg text-[#E0E0E0] focus:outline-0 focus:ring-2 focus:ring-[#4A90E2]/50 border border-[#2E2E3F] bg-[#0A0B14] focus:border-[#4A90E2]/50 h-10 placeholder:text-[#888888] px-3 text-sm" placeholder="Header Value" />
                      </div>
                      <button type="button" className="flex items-center gap-2 self-start text-sm text-[#4A90E2] hover:text-[#70AEE9] transition-colors">
                        <span className="material-symbols-outlined text-base">add</span>
                        Add Header
                      </button>
                    </div>
                  </div>
                </div>
              </details>
            </section>
          </div>

          {/* Action Bar */}
          <div className="mt-12 pt-6 border-t border-[#2E2E3F] flex items-center justify-end gap-4">
            <button 
              type="button" 
              className="px-5 py-2.5 rounded-lg text-[#E0E0E0] bg-[#131523] border border-[#2E2E3F] hover:bg-[#2E2E3F] transition-colors text-sm font-semibold"
              onClick={() => navigate('/dashboard')}
            >
              Cancel
            </button>
            <button 
              type="button" 
              disabled={isLoading || !selectedProject}
              className={`px-6 py-2.5 rounded-lg transition-colors shadow-lg text-sm font-semibold flex items-center gap-2 ${
                isLoading || !selectedProject
                  ? 'text-[#888888] bg-[#2E2E3F] cursor-not-allowed'
                  : 'text-[#0A0B14] bg-[#4A90E2] hover:bg-[#3b7bc2]'
              }`}
              onClick={handleStartScan}
            >
              {isLoading && (
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
              )}
              {isLoading ? 'Starting Scan...' : 'Start Scan'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ScanConfigPage;