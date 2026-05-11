import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { requireCurrentUser } from "./lib/auth";

export const list = query({
  args: { findingId: v.id("findings") },
  handler: async (ctx, args) => {
    await requireCurrentUser(ctx);
    const comments = await ctx.db.query("findingComments").withIndex("by_finding", (q) => q.eq("findingId", args.findingId)).collect();
    const users = await Promise.all(comments.map((comment) => ctx.db.get(comment.userId)));
    return comments.map((comment, index) => ({
      id: comment._id,
      content: comment.content,
      created_at: new Date(comment.createdAt).toISOString(),
      user_email: users[index]?.email ?? "User",
    }));
  },
});

export const add = mutation({
  args: { findingId: v.id("findings"), content: v.string() },
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);
    const id = await ctx.db.insert("findingComments", {
      findingId: args.findingId,
      userId: user._id,
      content: args.content,
      createdAt: Date.now(),
    });
    return {
      id,
      content: args.content,
      created_at: new Date().toISOString(),
      user_email: user.email ?? "User",
    };
  },
});
