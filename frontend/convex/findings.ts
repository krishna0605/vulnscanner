import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { requireCurrentUser } from "./lib/auth";

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
