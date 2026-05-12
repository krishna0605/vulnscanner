import { query } from "./_generated/server";
import type { QueryCtx } from "./_generated/server";
import { requireCurrentUser } from "./lib/auth";

export const inventory = query({
  args: {},
  handler: async (ctx) => buildInventory(ctx),
});

export const distribution = query({
  args: {},
  handler: async (ctx) => {
    const inventoryResult = await buildInventory(ctx);
    const grouped = new Map<string, { count: number; totalRisk: number }>();
    for (const asset of inventoryResult.assets) {
      const existing = grouped.get(asset.type) ?? { count: 0, totalRisk: 0 };
      existing.count += 1;
      existing.totalRisk += asset.riskScore ?? 0;
      grouped.set(asset.type, existing);
    }

    return Array.from(grouped.entries()).map(([type, stat]) => ({
      type,
      count: stat.count,
      riskLevel: stat.count ? Math.round(stat.totalRisk / stat.count) : 0,
    }));
  },
});

async function buildInventory(ctx: QueryCtx) {
  const user = await requireCurrentUser(ctx);
  const projects = await ctx.db.query("projects").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
  const projectById = new Map(projects.map((project) => [project._id, project]));
  const projectIds = new Set(projects.map((project: any) => project._id));
  const storedAssets = (await ctx.db.query("assets").collect()).filter((asset) => projectIds.has(asset.projectId));

  const assets = new Map<
    string,
    { name: string; type: string; project: string; status: string; lastScan: string; riskScore: number }
  >();

  for (const project of projects) {
    for (const target of project.targetUrls) {
      const hostname = hostnameFromUrl(target);
      if (!hostname) continue;
      assets.set(`${project._id}:${hostname}`, {
        name: hostname,
        type: "Domain",
        project: project.name,
        status: project.status === "active" ? "Active" : "Archived",
        lastScan: "Recently",
        riskScore: 0,
      });
    }
  }

  for (const asset of storedAssets) {
    const hostname = hostnameFromUrl(asset.url) ?? asset.url;
    const project = projectById.get(asset.projectId);
    assets.set(`${asset.projectId}:${hostname}`, {
      name: hostname,
      type: asset.type === "page" ? "Domain" : titleCase(asset.type),
      project: project?.name ?? "Unknown",
      status: asset.scanId ? "Discovered" : "Active",
      lastScan: asset.updatedAt ? new Date(asset.updatedAt).toISOString().slice(0, 10) : "Recently",
      riskScore: asset.riskScore ?? 0,
    });
  }

  const rows = Array.from(assets.values());
  const domains = rows.filter((asset) => asset.type === "Domain").length;

  return {
    totalAssets: rows.length,
    domains,
    subdomains: Math.max(0, rows.length - domains),
    ips: rows.filter((asset) => asset.type.toLowerCase() === "ip").length,
    assets: rows,
  };
}

function hostnameFromUrl(value: string) {
  try {
    return new URL(value).hostname;
  } catch {
    return value || null;
  }
}

function titleCase(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
