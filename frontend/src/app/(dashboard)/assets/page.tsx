import { Globe, Server, Database, Search, Filter, Layers } from 'lucide-react';
import { createClient } from '@/utils/supabase/server';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

async function getAssetStats() {
  const supabase = await createClient();

  // Get user's projects
  const { data: projects } = await supabase.from('projects').select('id, name, target_url');
  const projectIds = projects?.map((p) => p.id) || [];

  if (projectIds.length === 0) {
    return { totalAssets: 0, domains: 0, subdomains: 0, ips: 0, assets: [] };
  }

  // Get scans for user's projects to extract discovered assets
  const { data: scans } = await supabase
    .from('scans')
    .select('id, target_url, project_id')
    .in('project_id', projectIds);

  // Extract unique domains from projects and scans
  const domains = new Set<string>();
  const assets: Array<{
    name: string;
    type: string;
    project: string;
    status: string;
    lastScan: string;
  }> = [];

  projects?.forEach((p) => {
    try {
      const url = new URL(p.target_url);
      domains.add(url.hostname);
      assets.push({
        name: url.hostname,
        type: 'Domain',
        project: p.name,
        status: 'Active',
        lastScan: 'Recently',
      });
    } catch {}
  });

  scans?.forEach((s) => {
    try {
      const url = new URL(s.target_url);
      if (!domains.has(url.hostname)) {
        domains.add(url.hostname);
        const project = projects?.find((p) => p.id === s.project_id);
        assets.push({
          name: url.hostname,
          type: 'Subdomain',
          project: project?.name || 'Unknown',
          status: 'Discovered',
          lastScan: 'Pending',
        });
      }
    } catch {}
  });

  return {
    totalAssets: assets.length,
    domains: projects?.length || 0,
    subdomains: Math.max(0, assets.length - (projects?.length || 0)),
    ips: 0, // Would require additional discovery
    assets,
  };
}

export default async function AssetsPage() {
  const stats = await getAssetStats();

  return (
    <div className="max-w-[1600px] mx-auto animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-6">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Assets</h1>
          <p className="text-slate-400 text-lg font-light">
            Inventory of discovered assets, domains, and subdomains.
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <div className="glass-panel p-6 rounded-[24px] hover:bg-white/5 transition-colors group relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl -mr-6 -mt-6 transition-all group-hover:bg-cyan-500/20"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 group-hover:text-white transition-colors">
              <Layers className="h-6 w-6" />
            </div>
          </div>
          <h3 className="text-4xl font-bold text-white mb-1 tracking-tight">{stats.totalAssets}</h3>
          <p className="text-slate-400 text-sm font-medium">Total Assets</p>
        </div>

        <div className="glass-panel p-6 rounded-[24px] hover:bg-white/5 transition-colors group relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl -mr-6 -mt-6 transition-all group-hover:bg-blue-500/20"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 group-hover:text-white transition-colors">
              <Globe className="h-6 w-6" />
            </div>
          </div>
          <h3 className="text-4xl font-bold text-white mb-1 tracking-tight">{stats.domains}</h3>
          <p className="text-slate-400 text-sm font-medium">Domains</p>
        </div>

        <div className="glass-panel p-6 rounded-[24px] hover:bg-white/5 transition-colors group relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-violet-500/10 rounded-full blur-2xl -mr-6 -mt-6 transition-all group-hover:bg-violet-500/20"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 group-hover:text-white transition-colors">
              <Server className="h-6 w-6" />
            </div>
          </div>
          <h3 className="text-4xl font-bold text-white mb-1 tracking-tight">{stats.subdomains}</h3>
          <p className="text-slate-400 text-sm font-medium">Subdomains</p>
        </div>

        <div className="glass-panel p-6 rounded-[24px] hover:bg-white/5 transition-colors group relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl -mr-6 -mt-6 transition-all group-hover:bg-emerald-500/20"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 group-hover:text-white transition-colors">
              <Database className="h-6 w-6" />
            </div>
          </div>
          <h3 className="text-4xl font-bold text-white mb-1 tracking-tight">{stats.ips}</h3>
          <p className="text-slate-400 text-sm font-medium">IP Addresses</p>
        </div>
      </div>

      {/* Assets Table */}
      <div className="glass-panel rounded-[24px] overflow-hidden">
        <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
          <h3 className="text-xl font-bold text-white">Discovered Assets</h3>
          <div className="flex gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <Input
                placeholder="Search assets..."
                className="pl-10 bg-white/5 border-white/10 text-white w-64"
              />
            </div>
            <Button variant="outline" className="border-white/10 text-slate-400 hover:text-white">
              <Filter className="h-4 w-4 mr-2" /> Filter
            </Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-400">
            <thead className="text-[10px] uppercase bg-white/[0.02] text-slate-300 font-mono tracking-wider">
              <tr>
                <th className="px-6 py-4 font-medium" scope="col">
                  Asset Name
                </th>
                <th className="px-6 py-4 font-medium" scope="col">
                  Type
                </th>
                <th className="px-6 py-4 font-medium" scope="col">
                  Project
                </th>
                <th className="px-6 py-4 font-medium" scope="col">
                  Status
                </th>
                <th className="px-6 py-4 font-medium" scope="col">
                  Last Scan
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {stats.assets.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-12 text-slate-500 font-mono text-xs">
                    No assets discovered yet. Create a project and run a scan to discover assets.
                  </td>
                </tr>
              ) : (
                stats.assets.map((asset, i) => (
                  <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                          <Globe className="h-4 w-4 text-cyan-400" />
                        </div>
                        <span className="font-medium text-white">{asset.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase ${
                          asset.type === 'Domain'
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                            : 'bg-violet-500/10 text-violet-400 border border-violet-500/20'
                        }`}
                      >
                        {asset.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{asset.project}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded-full text-[10px] font-bold ${
                          asset.status === 'Active'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : 'bg-amber-500/10 text-amber-400'
                        }`}
                      >
                        {asset.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-500">{asset.lastScan}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
