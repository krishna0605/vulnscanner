import { action, mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { api, internal } from "./_generated/api";
import { getCurrentUser, requireCurrentUser } from "./lib/auth";

const scanType = v.union(v.literal("quick"), v.literal("standard"), v.literal("deep"), v.literal("full"));

export const listActive = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];
    const active = ["queued", "scanning", "processing", "paused"];
    const rows = await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    return rows.filter((scan) => active.includes(scan.status)).sort((a, b) => b.createdAt - a.createdAt);
  },
});

export const history = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    if (!user) return [];
    const rows = await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const scans = rows
      .filter((scan) => scan.status === "completed" || scan.status === "failed")
      .sort((a, b) => b.createdAt - a.createdAt)
      .slice(0, args.limit ?? 20);

    const result = [];
    for (const scan of scans) {
      const findings = await ctx.db.query("findings").withIndex("by_scan", (q) => q.eq("scanId", scan._id)).collect();
      const severityCounts = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
      for (const finding of findings) {
        severityCounts[finding.severity] += 1;
      }
      result.push({ ...scan, severityCounts, findingsCount: findings.length });
    }
    return result;
  },
});

export const stats = query({
  args: {},
  handler: async (ctx) => {
    const user = await getCurrentUser(ctx);
    if (!user) {
      return {
        monthCount: 0,
        avgDuration: "N/A",
        successRate: "100%",
      };
    }
    const scans = await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).getTime();
    const monthScans = scans.filter((scan) => scan.createdAt >= monthStart);
    const completed = monthScans.filter((scan) => scan.status === "completed");
    const successRate = monthScans.length ? Math.round((completed.length / monthScans.length) * 100) : 100;

    const durations = scans
      .filter((scan) => scan.status === "completed" && scan.completedAt)
      .slice(0, 50)
      .map((scan) => Math.max(0, Math.round(((scan.completedAt ?? scan.createdAt) - (scan.startedAt ?? scan.createdAt)) / 1000)));

    let avgDuration = "N/A";
    if (durations.length > 0) {
      const avgSeconds = Math.round(durations.reduce((total, seconds) => total + seconds, 0) / durations.length);
      avgDuration = avgSeconds < 60 ? `${avgSeconds}s` : `${Math.floor(avgSeconds / 60)}m ${avgSeconds % 60}s`;
    }

    return {
      monthCount: monthScans.length,
      avgDuration,
      successRate: `${successRate}%`,
    };
  },
});

export const get = query({
  args: { scanId: v.id("scans") },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const scan = await ctx.db.get(args.scanId);
    if (!scan || scan.ownerId !== user._id) throw new Error("Scan not found");
    const logs = await ctx.db.query("scanLogs").withIndex("by_scan_time", (q) => q.eq("scanId", args.scanId)).collect();
    const findings = await ctx.db.query("findings").withIndex("by_scan", (q) => q.eq("scanId", args.scanId)).collect();
    const assets = await ctx.db.query("assets").withIndex("by_scan", (q) => q.eq("scanId", args.scanId)).collect();
    return { scan, logs, findings, assets };
  },
});

export const start = action({
  args: {
    projectId: v.id("projects"),
    targetUrl: v.string(),
    config: v.optional(v.any()),
    type: v.optional(scanType),
  },
  handler: async (ctx, args): Promise<any> => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Unauthenticated");
    let user = await ctx.runQuery(internal.users.getByClerkId, { clerkId: identity.subject });
    if (!user) {
      user = await ctx.runMutation(internal.users.ensureFromIdentity, {
        clerkId: identity.subject,
        email: identity.email,
        name: identity.name ?? identity.nickname,
        avatarUrl: identity.pictureUrl,
      });
    }

    const scanId = await ctx.runMutation(internal.scanner.createQueuedScan, {
      ...args,
      ownerId: user._id,
    });
    const backendUrl = process.env.RAILWAY_BACKEND_URL;
    const token = process.env.SCANNER_SERVICE_TOKEN;
    if (!backendUrl || !token) {
      await ctx.runMutation(internal.scanner.failScan, {
        scanId,
        message: "Railway scanner is not configured",
      });
      return { id: scanId, status: "failed" };
    }

    const response = await fetch(`${backendUrl.replace(/\/$/, "")}/scanner/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        scanId,
        projectId: args.projectId,
        targetUrl: args.targetUrl,
        config: args.config ?? {},
      }),
    });

    if (!response.ok) {
      await ctx.runMutation(internal.scanner.failScan, {
        scanId,
        message: `Railway scanner dispatch failed: ${response.status}`,
      });
    }

    return { id: scanId, status: response.ok ? "queued" : "failed" };
  },
});

export const pause = mutation({
  args: { scanId: v.id("scans") },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const scan = await ctx.db.get(args.scanId);
    if (!scan || scan.ownerId !== user._id) throw new Error("Scan not found");
    await ctx.db.patch(args.scanId, { status: "paused", currentAction: "Paused by user", updatedAt: Date.now() });
    return { success: true };
  },
});

export const resume = mutation({
  args: { scanId: v.id("scans") },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const scan = await ctx.db.get(args.scanId);
    if (!scan || scan.ownerId !== user._id) throw new Error("Scan not found");
    await ctx.db.patch(args.scanId, { status: "scanning", currentAction: "Resuming...", updatedAt: Date.now() });
    return { success: true };
  },
});

export const cancel = mutation({
  args: { scanId: v.id("scans") },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const scan = await ctx.db.get(args.scanId);
    if (!scan || scan.ownerId !== user._id) throw new Error("Scan not found");
    await ctx.db.patch(args.scanId, {
      status: "cancelled",
      currentAction: "Cancelled by user",
      completedAt: Date.now(),
      updatedAt: Date.now(),
    });
    return { success: true };
  },
});
