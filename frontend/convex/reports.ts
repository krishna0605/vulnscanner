import { query } from "./_generated/server";
import { v } from "convex/values";
import { requireCurrentUser } from "./lib/auth";

async function ownedProjects(ctx: any, userId: any) {
  return await ctx.db.query("projects").withIndex("by_owner", (q: any) => q.eq("ownerId", userId)).collect();
}

export const globalStats = query({
  args: {},
  handler: async (ctx) => {
    const user = await requireCurrentUser(ctx);
    const projects = await ownedProjects(ctx, user._id);
    const projectIds = new Set(projects.map((project: any) => project._id));
    const scans = (await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect());
    const findings = (await ctx.db.query("findings").collect()).filter((finding) => projectIds.has(finding.projectId));
    const critical = findings.filter((finding) => finding.severity === "critical").length;
    const high = findings.filter((finding) => finding.severity === "high").length;
    const medium = findings.filter((finding) => finding.severity === "medium").length;
    const low = findings.filter((finding) => finding.severity === "low").length;
    const avgSecurityScore = Math.max(0, Math.min(100, 100 - critical * 15 - high * 8 - medium * 3 - low));

    return {
      total_scans: scans.length,
      total_projects: projects.length,
      critical_count: critical,
      high_count: high,
      avg_security_score: avgSecurityScore,
    };
  },
});

export const recentScans = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const scans = await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const projects = await ownedProjects(ctx, user._id);
    const projectById = new Map(projects.map((project: any) => [project._id, project]));
    return scans
      .sort((a, b) => b.createdAt - a.createdAt)
      .slice(0, args.limit ?? 20)
      .map((scan) => ({
        ...scan,
        project: { name: projectById.get(scan.projectId)?.name ?? "Unknown Project" },
        target_url: scan.targetUrl,
        created_at: new Date(scan.createdAt).toISOString(),
        completed_at: scan.completedAt ? new Date(scan.completedAt).toISOString() : null,
        findings_count: scan.findingsCount ?? 0,
        high_severity_count: scan.highSeverityCount ?? 0,
      }));
  },
});

export const scanReport = query({
  args: { scanId: v.id("scans") },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const scan = await ctx.db.get(args.scanId);
    if (!scan || scan.ownerId !== user._id) return null;
    const project = await ctx.db.get(scan.projectId);
    const findings = await ctx.db.query("findings").withIndex("by_scan", (q) => q.eq("scanId", args.scanId)).collect();
    const assets = await ctx.db.query("assets").withIndex("by_scan", (q) => q.eq("scanId", args.scanId)).collect();
    const severityDistribution = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
    const typeCounts = new Map<string, number>();

    for (const finding of findings) {
      severityDistribution[finding.severity] += 1;
      typeCounts.set(finding.title, (typeCounts.get(finding.title) ?? 0) + 1);
    }

    return {
      id: scan._id,
      created_at: new Date(scan.createdAt).toISOString(),
      target_url: scan.targetUrl,
      project_name: project?.name,
      status: scan.status,
      score: scan.score ?? 0,
      scan_duration_seconds: scan.completedAt && scan.startedAt ? Math.round((scan.completedAt - scan.startedAt) / 1000) : undefined,
      severity_distribution: severityDistribution,
      vulnerability_types: Array.from(typeCounts.entries()).map(([name, count]) => ({ name, count })),
      findings,
      assets: [{ count: assets.length }],
      completed_at: scan.completedAt ? new Date(scan.completedAt).toISOString() : undefined,
    };
  },
});
