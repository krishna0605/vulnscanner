import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { requireCurrentUser, requireProjectOwner } from "./lib/auth";

export const get = query({
  args: { findingId: v.id("findings") },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const finding = await ctx.db.get(args.findingId);
    if (!finding) return null;
    const project = await ctx.db.get(finding.projectId);
    if (!project || project.ownerId !== user._id) return null;
    const scan = await ctx.db.get(finding.scanId);
    return {
      ...finding,
      id: finding._id,
      scan_id: finding.scanId,
      project_id: finding.projectId,
      project_name: project.name,
      scan_created_at: scan ? new Date(scan.createdAt).toISOString() : "",
      created_at: new Date(finding.createdAt).toISOString(),
      cve_id: finding.cveId,
      cwe_id: finding.cweId,
      cvss_score: finding.cvssScore,
      reference_links: finding.referenceLinks,
      affected_assets: finding.affectedAssets,
    };
  },
});

export const related = query({
  args: { scanId: v.id("scans"), title: v.string(), severity: v.string() },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const scan = await ctx.db.get(args.scanId);
    if (!scan || scan.ownerId !== user._id) return [];
    return (await ctx.db.query("findings").withIndex("by_scan", (q) => q.eq("scanId", args.scanId)).collect())
      .filter((finding) => finding.title === args.title && finding.severity === args.severity);
  },
});

export const listOpen = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const projects = await ctx.db.query("projects").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const projectById = new Map(projects.map((project) => [project._id, project]));
    const projectIds = new Set(projects.map((project) => project._id));
    return (await ctx.db.query("findings").collect())
      .filter((finding) => projectIds.has(finding.projectId) && finding.status === "open")
      .sort((a, b) => b.createdAt - a.createdAt)
      .slice(0, args.limit ?? 20)
      .map((finding) => ({
        ...finding,
        id: finding._id,
        projectName: projectById.get(finding.projectId)?.name ?? "Unknown Project",
        detectedAt: new Date(finding.createdAt).toISOString(),
        cveId: finding.cveId,
      }));
  },
});

export const byProject = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    await requireProjectOwner(ctx, args.projectId);
    return (await ctx.db.query("findings").withIndex("by_project", (q) => q.eq("projectId", args.projectId)).collect())
      .filter((finding) => finding.status === "open")
      .sort((a, b) => b.createdAt - a.createdAt)
      .map((finding) => ({
        id: finding._id,
        title: finding.title,
        severity: finding.severity,
        status: finding.status,
        project_id: finding.projectId,
        created_at: new Date(finding.createdAt).toISOString(),
        location: finding.location ?? "Unknown",
      }));
  },
});

export const updateStatus = mutation({
  args: {
    findingId: v.id("findings"),
    status: v.union(v.literal("open"), v.literal("fixed"), v.literal("false_positive")),
  },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const finding = await ctx.db.get(args.findingId);
    if (!finding) throw new Error("Finding not found");
    const project = await ctx.db.get(finding.projectId);
    if (!project || project.ownerId !== user._id) throw new Error("Finding not found");
    await ctx.db.patch(args.findingId, { status: args.status, updatedAt: Date.now() });
    return { success: true };
  },
});
