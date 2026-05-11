import type { QueryCtx, MutationCtx } from "../_generated/server";

export async function getCurrentUser(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) {
    return null;
  }

  return await ctx.db
    .query("users")
    .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
    .unique();
}

export async function requireCurrentUser(ctx: QueryCtx | MutationCtx) {
  const user = await getCurrentUser(ctx);
  if (!user) {
    throw new Error("Unauthorized");
  }
  return user;
}

export async function requireProjectOwner(
  ctx: QueryCtx | MutationCtx,
  projectId: any,
) {
  const user = await requireCurrentUser(ctx);
  const project = await ctx.db.get(projectId);
  if (!project || project.ownerId !== user._id) {
    throw new Error("Project not found");
  }
  return { user, project };
}
