import { query } from "./_generated/server";
import { requireCurrentUser } from "./lib/auth";

export const stats = query({
  args: {},
  handler: async (ctx) => {
    const user = await requireCurrentUser(ctx);
    const scans = await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const projects = await ctx.db.query("projects").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const projectIds = new Set(projects.map((project) => project._id));
    const allFindings = await ctx.db.query("findings").collect();
    const findings = allFindings.filter((finding) => projectIds.has(finding.projectId));

    let critical = 0;
    let high = 0;
    let medium = 0;
    let low = 0;
    for (const finding of findings) {
      if (finding.severity === "critical") critical += 1;
      if (finding.severity === "high") high += 1;
      if (finding.severity === "medium") medium += 1;
      if (finding.severity === "low") low += 1;
    }

    const scoreFromFindings = Math.max(0, Math.min(100, 100 - critical * 15 - high * 8 - medium * 3 - low));
    const scoredScans = scans.filter((scan) => typeof scan.score === "number" && scan.score > 0);
    const securityScore =
      scoredScans.length > 0
        ? Math.floor(scoredScans.reduce((total, scan) => total + (scan.score ?? 0), 0) / scoredScans.length)
        : scoreFromFindings;
    const completedScans = scans.filter((scan) => scan.status === "completed").length;
    const failedScans = scans.filter((scan) => scan.status === "failed").length;
    const finished = completedScans + failedScans;

    return {
      securityScore,
      activeThreats: critical + high,
      completedScans,
      availability: finished > 0 ? Math.round((completedScans / finished) * 1000) / 10 : null,
    };
  },
});

export const graph = query({
  args: {},
  handler: async (ctx) => {
    const user = await requireCurrentUser(ctx);
    const projects = await ctx.db.query("projects").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const scans = await ctx.db.query("scans").withIndex("by_owner", (q) => q.eq("ownerId", user._id)).collect();
    const recentScans = scans.sort((a, b) => b.createdAt - a.createdAt).slice(0, 10);

    const nodes: any[] = [
      {
        id: "root-system",
        label: "VulnScanner",
        type: "root",
        val: 8,
        color: "#ffffff",
        data: { description: "Central Command" },
      },
    ];
    const links: any[] = [];

    for (const project of projects) {
      nodes.push({
        id: project._id,
        label: project.name,
        type: "project",
        val: 6,
        color: "#0ea5e9",
        data: project,
      });
      links.push({ source: project._id, target: "root-system", color: "rgba(255,255,255,0.15)" });
    }

    for (const scan of recentScans) {
      let color = "#8b5cf6";
      if (scan.status === "completed" && typeof scan.score === "number") {
        color = scan.score >= 80 ? "#22c55e" : scan.score >= 50 ? "#eab308" : "#ef4444";
      } else if (scan.status === "failed") {
        color = "#6b7280";
      }
      nodes.push({
        id: scan._id,
        label: scan.type || "Scan",
        type: "scan",
        val: 4,
        color,
        data: scan,
      });
      links.push({ source: scan._id, target: scan.projectId, color: "rgba(255,255,255,0.1)" });
    }

    return { nodes, links };
  },
});

export const activity = query({
  args: {},
  handler: async (ctx) => {
    const user = await requireCurrentUser(ctx);
    return await ctx.db
      .query("activityLogs")
      .withIndex("by_user_time", (q) => q.eq("userId", user._id))
      .order("desc")
      .take(10);
  },
});

export const metrics = query({
  args: {},
  handler: async (ctx) => {
    return (await ctx.db.query("systemMetrics").withIndex("by_timestamp").order("desc").take(20)).reverse();
  },
});
