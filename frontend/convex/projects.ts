import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { ensureCurrentUser, getCurrentUser, requireCurrentUser, requireProjectOwner } from "./lib/auth";

export const list = query({
  args: { status: v.optional(v.union(v.literal("active"), v.literal("archived"), v.literal("maintenance"))) },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];
    const rows = args.status
      ? await ctx.db
          .query("projects")
          .withIndex("by_owner_status", (q) => q.eq("ownerId", user._id).eq("status", args.status!))
          .collect()
      : await ctx.db.query("projects").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    return rows.sort((a, b) => b.createdAt - a.createdAt);
  },
});

export const get = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    const { project } = await requireProjectOwner(ctx, args.projectId);
    const scans = await ctx.db
      .query("scans")
      .withIndex("by_project_created", (q) => q.eq("projectId", args.projectId))
      .order("desc")
      .take(30);
    const latestScan = scans[0] ?? null;
    const findings = await ctx.db
      .query("findings")
      .withIndex("by_project_status", (q) => q.eq("projectId", args.projectId).eq("status", "open"))
      .collect();
    const assets = await ctx.db
      .query("assets")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
    const stats = { critical: 0, high: 0, medium: 0, low: 0, info: 0, total: findings.length };
    for (const finding of findings) {
      stats[finding.severity] += 1;
    }
    return {
      ...project,
      id: project._id,
      target_urls: project.targetUrls,
      lastScan: latestScan?.createdAt,
      lastScanStatus: latestScan?.status,
      securityScore: latestScan?.score ?? null,
      targets: project.targetUrls,
      scans,
      assets: assets.map((asset) => ({ ...asset, id: asset._id })),
      stats,
    };
  },
});

export const listWithStats = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];
    const projects = await ctx.db.query("projects").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const scans = await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const projectIds = new Set(projects.map((project) => project._id));
    const findings = (await ctx.db.query("findings").collect()).filter((finding) => projectIds.has(finding.projectId));

    return projects
      .sort((a, b) => b.createdAt - a.createdAt)
      .map((project) => {
        const projectScans = scans
          .filter((scan) => scan.projectId === project._id)
          .sort((a, b) => b.createdAt - a.createdAt);
        const latestScan = projectScans[0];
        const projectFindings = findings.filter((finding) => finding.projectId === project._id);
        const openFindings = projectFindings.filter((finding) => finding.status === "open");
        const severityCounts = { critical: 0, high: 0, medium: 0, low: 0, info: 0, total: openFindings.length };
        for (const finding of openFindings) {
          severityCounts[finding.severity] += 1;
        }
        const trend = projectScans.slice(0, 7).map((scan) => scan.score ?? 0);

        return {
          ...project,
          id: project._id,
          target_urls: project.targetUrls,
          target_url: project.targetUrls[0],
          scans: projectScans,
          findings: projectFindings,
          lastScan: latestScan?.completedAt ?? latestScan?.createdAt ?? project.createdAt,
          lastScanStatus: latestScan?.status ?? null,
          securityScore: latestScan?.score ?? null,
          trend,
          vulnerabilitiesCount: openFindings.length,
          stats: severityCounts,
        };
      });
  },
});

export const create = mutation({
  args: {
    name: v.string(),
    description: v.optional(v.string()),
    targetUrls: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args) => {
    const user = await ensureCurrentUser(ctx);
    const now = Date.now();
    const projectId = await ctx.db.insert("projects", {
      ownerId: user._id,
      name: args.name,
      description: args.description,
      status: "active",
      targetUrls: args.targetUrls ?? [],
      createdAt: now,
      updatedAt: now,
    });

    for (const url of args.targetUrls ?? []) {
      await ctx.db.insert("assets", {
        projectId,
        url,
        type: "page",
        createdAt: now,
        updatedAt: now,
      });
    }

    await ctx.db.insert("activityLogs", {
      userId: user._id,
      actionType: "project_created",
      description: `Created project ${args.name}`,
      metadata: { projectId },
      createdAt: now,
    });

    return await ctx.db.get(projectId);
  },
});

export const update = mutation({
  args: {
    projectId: v.id("projects"),
    name: v.string(),
    description: v.optional(v.string()),
    targetUrls: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args) => {
    await requireProjectOwner(ctx, args.projectId);
    await ctx.db.patch(args.projectId, {
      name: args.name,
      description: args.description,
      targetUrls: args.targetUrls ?? [],
      updatedAt: Date.now(),
    });
    return await ctx.db.get(args.projectId);
  },
});

export const remove = mutation({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    await requireProjectOwner(ctx, args.projectId);
    await ctx.db.patch(args.projectId, { status: "archived", updatedAt: Date.now() });
    return { deleted: true };
  },
});
