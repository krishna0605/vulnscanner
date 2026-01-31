import { getReportsGlobalStats, getReportsScans } from '@/lib/api';
import { ReportsHubStats } from '@/components/reports/reports-hub-stats';
import { ScansList } from '@/components/reports/scans-list';

export default async function ReportsHub() {
  const [stats, scans] = await Promise.all([getReportsGlobalStats(), getReportsScans()]);

  return (
    <div className="max-w-[1600px] mx-auto animate-in fade-in duration-700">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Security Reports</h1>
        <p className="text-slate-400 text-lg font-light">
          Overview of your security posture across all completed scans.
        </p>
      </div>

      <ReportsHubStats stats={stats} />

      <div className="mt-12">
        <h2 className="text-2xl font-bold text-white mb-6">Recent Scans</h2>
        <ScansList scans={scans} />
      </div>
    </div>
  );
}
