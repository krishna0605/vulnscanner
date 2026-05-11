import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { requireProjectOwner } from "./lib/auth";

export const upsert = mutation({
  args: {
    projectId: v.id("projects"),
    type: v.union(v.literal("jira"), v.literal("github")),
    config: v.any(),
  },
  handler: async (ctx, args) => {
    await requireProjectOwner(ctx, args.projectId);
    const now = Date.now();
    const existing = await ctx.db
      .query("integrations")
      .withIndex("by_project_type", (q) => q.eq("projectId", args.projectId).eq("type", args.type))
      .unique();
    if (existing) {
      await ctx.db.patch(existing._id, { config: args.config, updatedAt: now });
      return existing._id;
    }
    return await ctx.db.insert("integrations", {
      projectId: args.projectId,
      type: args.type,
      config: args.config,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const get = query({
  args: { projectId: v.id("projects"), type: v.union(v.literal("jira"), v.literal("github")) },
  handler: async (ctx, args) => {
    await requireProjectOwner(ctx, args.projectId);
    return await ctx.db
      .query("integrations")
      .withIndex("by_project_type", (q) => q.eq("projectId", args.projectId).eq("type", args.type))
      .unique();
  },
});
