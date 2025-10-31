import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import projectService, { ProjectCreate } from '../services/projectService.ts';

const CreateProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<ProjectCreate>({
    name: '',
    description: '',
    target_domain: '',
    scope_rules: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null); // Clear error when user starts typing
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.name.trim()) {
        throw new Error('Project name is required');
      }
      if (!formData.target_domain.trim()) {
        throw new Error('Target domain is required');
      }

      // Create the project
      await projectService.createProject({
        name: formData.name.trim(),
        description: formData.description?.trim() || undefined,
        target_domain: formData.target_domain.trim(),
        scope_rules: formData.scope_rules
      });

      // Navigate back to dashboard on success
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full">
      {/* Background grid and aurora accents */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-transparent bg-[radial-gradient(#1A1A2E_1px,transparent_1px)] [background-size:32px_32px]" />
      <div className="absolute top-0 left-0 -z-10 h-1/2 w-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(74,144,226,0.14),rgba(255,255,255,0))]" />

      {/* Top navbar (simple) */}
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

      {/* Create Project Card */}
      <main className="flex flex-1 justify-center py-10 px-4 sm:px-6 lg:px-10">
        <div className="relative z-10 w-full max-w-lg rounded-lg border border-[#2E2E3F]/60 bg-[#131523]/80 p-8 shadow-2xl shadow-black/50 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-2 mb-8">
            <div className="flex items-center justify-center h-14 w-14 rounded-full border border-[#4A90E2]/40 bg-[#4A90E2]/10 text-[#4A90E2]">
              <span className="material-symbols-outlined text-3xl">add_circle</span>
            </div>
            <h1 className="text-white text-2xl font-medium tracking-wide">Create New Project</h1>
            <p className="text-[#888888] text-sm">Configure and launch a new vulnerability scan</p>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-md bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="project-name">Project Name</label>
              <div className="glow-on-focus relative flex items-center rounded-md border border-[#2E2E3F] bg-[#0A0B14] transition-all">
                <span className="material-symbols-outlined text-[#888888] absolute left-3 text-xl">label</span>
                <input 
                  className="form-input w-full bg-transparent h-11 pl-10 pr-4 text-[#E0E0E0] placeholder:text-[#888888] focus:outline-none focus:ring-0 text-base" 
                  id="project-name" 
                  name="name"
                  placeholder="e.g., Main Website Audit" 
                  type="text" 
                  value={formData.name}
                  onChange={handleInputChange}
                  required 
                />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="description">Description</label>
              <div className="glow-on-focus relative flex items-start rounded-md border border-[#2E2E3F] bg-[#0A0B14] transition-all pt-3">
                <span className="material-symbols-outlined text-[#888888] absolute left-3 text-xl">description</span>
                <textarea 
                  className="form-textarea w-full bg-transparent pl-10 pr-4 py-3 text-[#E0E0E0] placeholder:text-[#888888] focus:outline-none focus:ring-0 text-base resize-none" 
                  id="description" 
                  name="description"
                  placeholder="Brief description of the project scope and objectives" 
                  rows={3}
                  value={formData.description || ''}
                  onChange={handleInputChange}
                />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="target-domain">Target Domain</label>
              <div className="glow-on-focus relative flex items-center rounded-md border border-[#2E2E3F] bg-[#0A0B14] transition-all">
                <span className="material-symbols-outlined text-[#888888] absolute left-3 text-xl">public</span>
                <input 
                  className="form-input w-full bg-transparent h-11 pl-10 pr-4 text-[#E0E0E0] placeholder:text-[#888888] focus:outline-none focus:ring-0 text-base" 
                  id="target-domain" 
                  name="target_domain"
                  placeholder="e.g., https://example.com" 
                  type="url" 
                  value={formData.target_domain}
                  onChange={handleInputChange}
                  required 
                />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="scan-settings">Scan Settings</label>
              <div className="glow-on-focus relative flex items-center rounded-md border border-[#2E2E3F] bg-[#0A0B14] transition-all">
                <span className="material-symbols-outlined text-[#888888] absolute left-3 text-xl">tune</span>
                <select className="form-select w-full bg-transparent h-11 pl-10 pr-10 text-[#E0E0E0] focus:outline-none focus:ring-0 text-base" id="scan-settings" defaultValue="comprehensive">
                  <option className="bg-[#0A0B14]" value="comprehensive">Comprehensive Scan</option>
                  <option className="bg-[#0A0B14]" value="quick">Quick Scan</option>
                  <option className="bg-[#0A0B14]" value="owasp_top_10">OWASP Top 10</option>
                  <option className="bg-[#0A0B14]" value="custom">Custom Profile</option>
                </select>
                <span className="material-symbols-outlined text-[#888888] absolute right-3">expand_more</span>
              </div>
            </div>
            <div className="pt-4 flex items-center justify-end gap-4">
              <button type="button" className="flex h-11 items-center justify-center rounded-md px-6 text-sm font-medium text-[#888888] hover:text-white" onClick={() => navigate('/dashboard')}>Cancel</button>
              <button type="submit" className="relative flex w-44 items-center justify-center overflow-hidden rounded-md h-11 px-5 text-base font-medium tracking-wide text-white bg-[#4A90E2]/20 border border-[#4A90E2]/40 hover:bg-[#4A90E2]/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" disabled={isLoading}>
                <span>{isLoading ? 'Creating...' : 'Create Project'}</span>
              </button>
            </div>
          </form>
          <div className="pt-4">
            <p className="text-xs text-[#888888]">© 2024 SecureScan Dynamics. All rights reserved.</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CreateProjectPage;