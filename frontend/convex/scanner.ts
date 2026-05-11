import { internalMutation, internalQuery } from "./_generated/server";
import { v } from "convex/values";

const truncate = (value: string | undefined, max = 2000) =>
  value ? value.slice(0, max) : undefined;

export const createQueuedScan = internalMutation({
  args: {
    projectId: v.id("projects"),
    ownerId: v.id("users"),
    targetUrl: v.string(),
    config: v.optional(v.any()),
    type: v.optional(v.union(v.literal("quick"), v.literal("standard"), v.literal("deep"), v.literal("full"))),
  },
  handler: async (ctx, args) => {
    const project = await ctx.db.get(args.projectId);
    if (!project || project.ownerId !== args.ownerId) {
      throw new Error("Project not found");
    }
    const now = Date.now();
    const scanId = await ctx.db.insert("scans", {
      projectId: args.projectId,
      ownerId: args.ownerId,
      targetUrl: args.targetUrl,
      status: "queued",
      type: args.type ?? args.config?.scanType ?? "quick",
      config: args.config ?? {},
      progress: 0,
      currentAction: "Queued",
      score: 0,
      findingsCount: 0,
      highSeverityCount: 0,
      createdAt: now,
      updatedAt: now,
    });
    await ctx.db.insert("activityLogs", {
      userId: args.ownerId,
      actionType: "scan_queued",
      description: `Queued scan for ${args.targetUrl}`,
      metadata: { scanId, projectId: args.projectId },
      createdAt: now,
    });
    return scanId;
  },
});

export const status = internalQuery({
  args: { scanId: v.id("scans") },
  handler: async (ctx, args) => {
    const scan = await ctx.db.get(args.scanId);
    return scan ? { status: scan.status } : null;
  },
});

export const markStarted = internalMutation({
  args: { scanId: v.id("scans"), node: v.optional(v.string()) },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.scanId, {
      status: "scanning",
      node: args.node,
      currentAction: "Launching engine...",
      startedAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});

export const updateProgress = internalMutation({
  args: {
    scanId: v.id("scans"),
    progress: v.number(),
    currentAction: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.scanId, {
      status: args.progress >= 100 ? "completed" : "scanning",
      progress: Math.max(0, Math.min(100, args.progress)),
      currentAction: truncate(args.currentAction, 240),
      updatedAt: Date.now(),
    });
  },
});

export const addLog = internalMutation({
  args: {
    scanId: v.id("scans"),
    message: v.string(),
    level: v.union(v.literal("info"), v.literal("warn"), v.literal("error"), v.literal("success")),
    timestamp: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("scanLogs", {
      scanId: args.scanId,
      level: args.level,
      message: truncate(args.message, 500) ?? "",
      timestamp: args.timestamp ?? Date.now(),
    });
  },
});

export const addAsset = internalMutation({
  args: {
    projectId: v.id("projects"),
    scanId: v.optional(v.id("scans")),
    url: v.string(),
    type: v.string(),
    statusCode: v.optional(v.number()),
    title: v.optional(v.string()),
    metadata: v.optional(v.any()),
    riskScore: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    if (args.scanId) {
      const existing = (await ctx.db
        .query("assets")
        .withIndex("by_scan", (q) => q.eq("scanId", args.scanId))
        .collect())
        .find((asset) => asset.url === args.url && asset.type === args.type);

      if (existing) {
        await ctx.db.patch(existing._id, {
          statusCode: args.statusCode,
          title: truncate(args.title, 200),
          metadata: args.metadata,
          riskScore: args.riskScore,
          updatedAt: now,
        });
        return existing._id;
      }
    }

    return await ctx.db.insert("assets", {
      projectId: args.projectId,
      scanId: args.scanId,
      url: args.url,
      type: args.type,
      statusCode: args.statusCode,
      title: truncate(args.title, 200),
      metadata: args.metadata,
      riskScore: args.riskScore,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const addFinding = internalMutation({
  args: {
    scanId: v.id("scans"),
    projectId: v.id("projects"),
    title: v.string(),
    description: v.optional(v.string()),
    severity: v.union(v.literal("critical"), v.literal("high"), v.literal("medium"), v.literal("low"), v.literal("info")),
    location: v.optional(v.string()),
    evidence: v.optional(v.string()),
    remediation: v.optional(v.string()),
    cweId: v.optional(v.string()),
    cveId: v.optional(v.string()),
    cvssScore: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    const id = await ctx.db.insert("findings", {
      scanId: args.scanId,
      projectId: args.projectId,
      title: truncate(args.title, 200) ?? "Finding",
      description: truncate(args.description, 2000),
      severity: args.severity,
      status: "open",
      location: truncate(args.location, 500),
      evidence: truncate(args.evidence, 2000),
      remediation: truncate(args.remediation, 2000),
      cweId: args.cweId,
      cveId: args.cveId,
      cvssScore: args.cvssScore,
      createdAt: now,
      updatedAt: now,
    });
    const scan = await ctx.db.get(args.scanId);
    if (scan) {
      const highSeverityCount =
        (scan.highSeverityCount ?? 0) + (args.severity === "critical" || args.severity === "high" ? 1 : 0);
      await ctx.db.patch(args.scanId, {
        findingsCount: (scan.findingsCount ?? 0) + 1,
        highSeverityCount,
        updatedAt: now,
      });
    }
    return id;
  },
});

export const completeScan = internalMutation({
  args: { scanId: v.id("scans"), score: v.optional(v.number()) },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.scanId, {
      status: "completed",
      progress: 100,
      currentAction: "Completed",
      score: args.score,
      completedAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});

export const failScan = internalMutation({
  args: { scanId: v.id("scans"), message: v.string() },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.scanId, {
      status: "failed",
      currentAction: truncate(args.message, 240),
      completedAt: Date.now(),
      updatedAt: Date.now(),
    });
  },
});
