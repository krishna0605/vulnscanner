import { Suspense } from 'react';
import { Download, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import {
  getProjectsTableData,
  getGlobalVulnerabilities,
  getTeamStats,
  getAssetDistribution,
  getProjectsPageStats,
} from '@/lib/api';
import { ProjectsTable } from '@/components/projects/projects-table';
import { TeamCard } from '@/components/projects/team-card';
import { AssetDistributionCard } from '@/components/projects/asset-distribution';
import { GlobalVulnerabilityTable } from '@/components/projects/global-vuln-table';
import {
  MotionContainer,
  MotionItem,
  GlassCard,
  MotionDiv,
} from '@/components/projects/motion-wrapper';

export const dynamic = 'force-dynamic';

export default async function ProjectsPage() {
  const [projects, globalVulns, team, assets, stats] = await Promise.all([
    getProjectsTableData(),
    getGlobalVulnerabilities(),
    getTeamStats(),
    getAssetDistribution(),
    getProjectsPageStats(),
  ]);

  return (
    <div className="min-h-screen p-4 md:p-8 relative overflow-hidden">
      {/* Ambient Background Glows */}
      <div className="fixed top-0 left-0 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[120px] -z-10 mix-blend-screen pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px] -z-10 mix-blend-screen pointer-events-none" />

      <MotionContainer className="max-w-[1920px] mx-auto space-y-8">
        {/* Header */}
        <MotionItem className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <MotionDiv
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              className="flex items-center gap-4 mb-2"
            >
              <div className="p-3 bg-gradient-to-br from-cyan-500/20 to-blue-600/10 rounded-2xl border border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.15)]">
                <span className="material-symbols-outlined text-cyan-400 text-2xl">
                  folder_managed
                </span>
              </div>
              <div>
                <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 tracking-tight">
                  Mission Control
                </h1>
                <div className="h-1 w-12 bg-cyan-500 rounded-full mt-1"></div>
              </div>
            </MotionDiv>
            <p className="text-slate-400 text-sm max-w-xl pl-1">
              Real-time operational intelligence. Monitor project health, team velocity, and
              cross-functional security risks.
            </p>
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              className="h-11 px-5 rounded-xl border border-white/5 bg-white/[0.02] text-slate-300 hover:text-white hover:bg-white/[0.1] backdrop-blur-md transition-all"
            >
              <Download className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Export Intelligence</span>
            </Button>
            <Link href="/projects/new">
              <Button className="h-11 px-7 rounded-xl bg-white text-black font-bold text-sm hover:scale-105 transition-transform shadow-[0_0_30px_rgba(255,255,255,0.3)]">
                <Plus className="h-4 w-4 mr-2" />
                New Project
              </Button>
            </Link>
          </div>
        </MotionItem>

        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <MotionItem>
            <GlassCard className="p-6 h-full group" hoverEffect={true}>
              <div className="absolute top-0 right-0 p-5 opacity-5 group-hover:opacity-10 transition-opacity duration-500 scale-150 rotate-12 origin-top-right">
                <span className="material-symbols-outlined text-6xl">inventory_2</span>
              </div>
              <div className="flex flex-col justify-between h-full">
                <div>
                  <p className="text-[11px] text-cyan-200/60 font-mono uppercase tracking-widest mb-2 font-semibold">
                    Active Projects
                  </p>
                  <div className="flex items-baseline gap-2">
                    <h2 className="text-4xl font-bold text-white tracking-tighter">
                      {stats.projectCount}
                    </h2>
                    {stats.projectCountChange !== 0 && (
                      <span
                        className={`text-sm font-medium ${stats.projectCountChange > 0 ? 'text-emerald-400' : 'text-red-400'}`}
                      >
                        {stats.projectCountChange > 0 ? '+' : ''}
                        {stats.projectCountChange}
                      </span>
                    )}
                  </div>
                </div>
                <div className="mt-4 w-full h-1 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-cyan-500 w-[70%] shadow-[0_0_10px_#06b6d4]"></div>
                </div>
              </div>
            </GlassCard>
          </MotionItem>

          <MotionItem>
            <GlassCard className="p-6 h-full group" hoverEffect={true}>
              <div className="absolute top-0 right-0 p-5 opacity-5 group-hover:opacity-10 transition-opacity duration-500 scale-150 rotate-12 origin-top-right">
                <span className="material-symbols-outlined text-6xl">bug_report</span>
              </div>
              <div>
                <p className="text-[11px] text-red-200/60 font-mono uppercase tracking-widest mb-2 font-semibold">
                  Critical Risks
                </p>
                <div className="flex items-baseline gap-2">
                  <h2 className="text-4xl font-bold text-white tracking-tighter">
                    {stats.criticalRisksCount}
                  </h2>
                  <span className="text-sm text-slate-500">
                    {stats.criticalRisksCount === 1 ? 'Issue' : 'Issues'}
                  </span>
                </div>
              </div>
              <div className="mt-4 flex gap-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className={`h-1.5 w-full rounded-full ${i < 3 ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-white/10'}`}
                  ></div>
                ))}
              </div>
            </GlassCard>
          </MotionItem>

          <MotionItem>
            <GlassCard className="p-6 h-full group" hoverEffect={true}>
              <div className="absolute top-0 right-0 p-5 opacity-5 group-hover:opacity-10 transition-opacity duration-500 scale-150 rotate-12 origin-top-right">
                <span className="material-symbols-outlined text-6xl">verified_user</span>
              </div>
              <div>
                <p className="text-[11px] text-emerald-200/60 font-mono uppercase tracking-widest mb-2 font-semibold">
                  Security Score
                </p>
                <div className="flex items-baseline gap-2">
                  <h2 className="text-4xl font-bold text-white tracking-tighter">
                    {stats.avgSecurityScore !== null ? `${stats.avgSecurityScore}%` : '--'}
                  </h2>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-3">
                <span
                  className={`material-symbols-outlined text-xl ${stats.avgSecurityScore !== null && stats.avgSecurityScore >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}
                >
                  {stats.avgSecurityScore !== null && stats.avgSecurityScore >= 80
                    ? 'trending_up'
                    : 'trending_flat'}
                </span>
                <span className="text-xs text-slate-400">
                  {stats.avgSecurityScore !== null
                    ? stats.avgSecurityScore >= 80
                      ? 'Healthy Posture'
                      : 'Needs Attention'
                    : 'No Data'}
                </span>
              </div>
            </GlassCard>
          </MotionItem>

          <MotionItem>
            <GlassCard className="p-6 h-full group" hoverEffect={true}>
              <div className="absolute top-0 right-0 p-5 opacity-5 group-hover:opacity-10 transition-opacity duration-500 scale-150 rotate-12 origin-top-right">
                <span className="material-symbols-outlined text-6xl">bolt</span>
              </div>
              <div>
                <p className="text-[11px] text-amber-200/60 font-mono uppercase tracking-widest mb-2 font-semibold">
                  Fix Velocity
                </p>
                <h2 className="text-4xl font-bold text-white tracking-tighter">
                  {stats.fixVelocity ?? '--'}
                </h2>
              </div>
              <div className="mt-4 bg-white/5 rounded-lg p-2 border border-white/5 flex items-center justify-between">
                <span className="text-[10px] text-slate-400">Avg Time to Fix</span>
                <span className="text-xs text-white font-mono">
                  {stats.avgTimeToFixDays !== null ? `${stats.avgTimeToFixDays} Days` : 'N/A'}
                </span>
              </div>
            </GlassCard>
          </MotionItem>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
          {/* Left Main (Table) */}
          <div className="xl:col-span-8 flex flex-col gap-6">
            <MotionItem>
              <div className="flex items-center gap-3 mb-2 px-2">
                <div className="h-2 w-2 rounded-full bg-cyan-500 shadow-[0_0_10px_#06b6d4]"></div>
                <h2 className="text-sm font-bold text-slate-300 uppercase tracking-widest">
                  Active Portfolios
                </h2>
              </div>
              <GlassCard className="p-0 border-none" hoverEffect={false}>
                <ProjectsTable data={projects} />
              </GlassCard>
            </MotionItem>

            <MotionItem>
              <div className="flex items-center gap-3 mb-2 px-2 mt-4">
                <div className="h-2 w-2 rounded-full bg-red-500 shadow-[0_0_10px_#ef4444]"></div>
                <h2 className="text-sm font-bold text-slate-300 uppercase tracking-widest">
                  Critical Intelligence Stream
                </h2>
              </div>
              <GlassCard className="p-0" hoverEffect={false}>
                <GlobalVulnerabilityTable vulns={globalVulns} />
              </GlassCard>
            </MotionItem>
          </div>

          {/* Right Side Widgets */}
          <div className="xl:col-span-4 flex flex-col gap-6">
            {/* Decorative Ad/Tip */}
            <MotionItem>
              <GlassCard className="p-6 bg-gradient-to-br from-indigo-900/40 to-purple-900/40 border-indigo-500/30">
                <h3 className="text-white font-bold mb-2">Pro Tip</h3>
                <p className="text-xs text-indigo-200 leading-relaxed">
                  Integrate your CI/CD pipeline to enable real-time commit scanning.
                </p>
                <Button
                  variant="link"
                  className="text-indigo-300 text-xs p-0 mt-3 h-auto hover:text-white"
                >
                  Configure Integrations &rarr;
                </Button>
              </GlassCard>
            </MotionItem>
          </div>
        </div>
      </MotionContainer>
    </div>
  );
}
