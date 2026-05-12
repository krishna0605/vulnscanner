import type { QueryCtx, MutationCtx } from "../_generated/server";
import type { Id } from "../_generated/dataModel";

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

export async function ensureCurrentUser(ctx: MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) {
    throw new Error("Unauthorized");
  }

  const now = Date.now();
  const existing = await ctx.db
    .query("users")
    .withIndex("by_clerk_id", (q) => q.eq("clerkId", identity.subject))
    .unique();

  const email = identity.email;
  const name = identity.name ?? identity.nickname;
  const avatarUrl = identity.pictureUrl;

  if (existing) {
    await ctx.db.patch(existing._id, {
      email,
      name,
      avatarUrl,
      updatedAt: now,
    });
    return (await ctx.db.get(existing._id))!;
  }

  const userId = await ctx.db.insert("users", {
    clerkId: identity.subject,
    email,
    name,
    avatarUrl,
    role: "user",
    plan: "Free Plan",
    createdAt: now,
    updatedAt: now,
  });

  return (await ctx.db.get(userId))!;
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
  projectId: Id<"projects">,
) {
  const user = await requireCurrentUser(ctx);
  const project = await ctx.db.get(projectId);
  if (!project || project.ownerId !== user._id) {
    throw new Error("Project not found");
  }
  return { user, project };
}
