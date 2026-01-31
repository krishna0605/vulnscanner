import { createClient } from '@/utils/supabase/server';
import { redirect } from 'next/navigation';
import { SecurityScoreGauge } from '@/components/dashboard/security-score';
import {
  ActiveThreatCard,
  CurrentScansCard,
  AvailabilityCard,
} from '@/components/dashboard/stat-cards';
// import { NetworkTrafficChart } from '@/components/dashboard/network-chart'
import { VulnerabilityGraph } from '@/components/dashboard/vulnerability-graph';
import { RecentActivityFeed } from '@/components/dashboard/activity-feed';
import { ProjectsList } from '@/components/dashboard/projects-list';
import {
  getDashboardStats,
  getNetworkMetrics,
  getRecentActivity,
  getDashboardProjects,
  getGraphData,
} from '@/lib/api';

export const dynamic = 'force-dynamic'; // Ensure real-time data fetching

export default async function DashboardPage() {
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return redirect('/login');
  }

  const displayName = user.user_metadata?.full_name || user.email?.split('@')[0] || 'Admin';

  // Fetch Dashboard Data
  const stats = await getDashboardStats();
  // const networkData = await getNetworkMetrics() // Replaced by Graph
  const graphData = await getGraphData();
  const activityLogs = await getRecentActivity();
  const projects = await getDashboardProjects();

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-4xl font-sans font-bold text-white mb-2 tracking-tight">Dashboard</h1>
          <p className="text-slate-400 text-lg font-light">
            Welcome back, <span className="text-white font-medium">{displayName}</span>. Here’s your
            security posture.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Top Row: Gauge + Cards */}
        <SecurityScoreGauge score={stats.securityScore} />

        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
          <ActiveThreatCard count={stats.activeThreats} />
          <CurrentScansCard count={stats.completedScans} />
          <AvailabilityCard score={stats.availability} />
        </div>

        {/* Middle Row: Graph + Feed */}
        <div className="lg:col-span-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Replaced NetworkTrafficChart with VulnerabilityGraph */}
          <VulnerabilityGraph data={graphData} />

          <div className="lg:col-span-1">
            <RecentActivityFeed logs={activityLogs} />
          </div>
        </div>

        {/* Bottom Row: Projects */}
        <div className="lg:col-span-4">
          <ProjectsList projects={projects} />
        </div>
      </div>
    </div>
  );
}
