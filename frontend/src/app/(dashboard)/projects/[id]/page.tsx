import {
  getProjectDetails,
  getProjectTrend,
  getProjectVulnerabilities,
  getProjectRecentScans,
} from '@/lib/api';
import { ProjectHeader } from '@/components/projects/project-details/project-header';
import { VulnerabilityTrend } from '@/components/projects/project-details/vulnerability-trend';
import { DiscoveredVulnsTable } from '@/components/projects/project-details/discovered-vulns-table';
import { RecentScansCard } from '@/components/projects/project-details/recent-scans-card';
import { redirect } from 'next/navigation';

export const dynamic = 'force-dynamic';

interface PageProps {
  params: {
    id: string;
  };
}

export default async function ProjectDetailsPage({ params }: PageProps) {
  const [project, trend, vulns, recentScans] = await Promise.all([
    getProjectDetails(params.id),
    getProjectTrend(params.id),
    getProjectVulnerabilities(params.id),
    getProjectRecentScans(params.id),
  ]);

  if (!project) {
    redirect('/projects');
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-[#313131]">
      {' '}
      {/* Fixed bg color matching reference */}
      {/* Background Elements from Reference */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-[#313131]"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-gradient-to-br from-[#313131] via-[#414141] to-[#313131] opacity-80"></div>
      <div className="fixed top-[-20%] left-[-10%] w-[600px] h-[600px] bg-white/5 rounded-full blur-[120px] animate-drift"></div>
      <div
        className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-gray-500/10 rounded-full blur-[120px] animate-drift"
        style={{ animationDelay: '-5s' }}
      ></div>
      <div className="relative pt-8 pb-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex items-center space-x-2 text-sm text-slate-500 mb-2 font-mono">
          <span className="hover:text-white transition-colors cursor-pointer">PROJECTS</span>
          <span className="material-symbols-outlined text-sm">chevron_right</span>
          <span className="text-white uppercase">{project.name}</span>
        </div>

        {/* Header */}
        <ProjectHeader project={project} />

        {/* Main Content Grid matching reference (8 and 4) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left: Trend */}
          <div className="lg:col-span-8 flex flex-col h-full">
            <div className="h-full">
              <VulnerabilityTrend data={trend} />
            </div>
          </div>

          {/* Right: Recent Scans (No Team Members) */}
          <div className="lg:col-span-4 flex flex-col h-full">
            <RecentScansCard scans={recentScans} />
          </div>
        </div>

        {/* Vulns Table */}
        <DiscoveredVulnsTable vulns={vulns} />
      </div>
    </div>
  );
}
