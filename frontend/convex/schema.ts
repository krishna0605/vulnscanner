import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

const status = v.union(
  v.literal("queued"),
  v.literal("scanning"),
  v.literal("processing"),
  v.literal("paused"),
  v.literal("completed"),
  v.literal("failed"),
  v.literal("cancelled")
);

const severity = v.union(
  v.literal("critical"),
  v.literal("high"),
  v.literal("medium"),
  v.literal("low"),
  v.literal("info")
);

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    email: v.optional(v.string()),
    name: v.optional(v.string()),
    avatarUrl: v.optional(v.string()),
    role: v.optional(v.string()),
    plan: v.optional(v.string()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_clerk_id", ["clerkId"])
    .index("by_email", ["email"]),

  projects: defineTable({
    ownerId: v.id("users"),
    name: v.string(),
    description: v.optional(v.string()),
    status: v.union(v.literal("active"), v.literal("archived"), v.literal("maintenance")),
    targetUrls: v.array(v.string()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_owner", ["ownerId"])
    .index("by_owner_status", ["ownerId", "status"]),

  assets: defineTable({
    projectId: v.id("projects"),
    scanId: v.optional(v.id("scans")),
    url: v.string(),
    type: v.string(),
    statusCode: v.optional(v.number()),
    title: v.optional(v.string()),
    metadata: v.optional(v.any()),
    riskScore: v.optional(v.number()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_project", ["projectId"])
    .index("by_scan", ["scanId"]),

  scans: defineTable({
    projectId: v.id("projects"),
    ownerId: v.id("users"),
    targetUrl: v.string(),
    status,
    type: v.union(v.literal("quick"), v.literal("standard"), v.literal("full"), v.literal("deep"), v.literal("credentialed")),
    config: v.optional(v.any()),
    progress: v.number(),
    currentAction: v.optional(v.string()),
    score: v.optional(v.number()),
    findingsCount: v.optional(v.number()),
    highSeverityCount: v.optional(v.number()),
    node: v.optional(v.string()),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_project", ["projectId"])
    .index("by_owner", ["ownerId"])
    .index("by_owner_status", ["ownerId", "status"])
    .index("by_project_created", ["projectId", "createdAt"]),

  scanLogs: defineTable({
    scanId: v.id("scans"),
    level: v.union(v.literal("info"), v.literal("warn"), v.literal("error"), v.literal("success")),
    message: v.string(),
    timestamp: v.number(),
  }).index("by_scan_time", ["scanId", "timestamp"]),

  findings: defineTable({
    scanId: v.id("scans"),
    projectId: v.id("projects"),
    title: v.string(),
    description: v.optional(v.string()),
    severity,
    status: v.union(v.literal("open"), v.literal("fixed"), v.literal("false_positive"), v.literal("resolved"), v.literal("ignored")),
    location: v.optional(v.string()),
    evidence: v.optional(v.string()),
    remediation: v.optional(v.string()),
    cveId: v.optional(v.string()),
    cweId: v.optional(v.string()),
    cvssScore: v.optional(v.number()),
    referenceLinks: v.optional(v.any()),
    affectedAssets: v.optional(v.any()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_scan", ["scanId"])
    .index("by_project", ["projectId"])
    .index("by_project_status", ["projectId", "status"])
    .index("by_scan_severity", ["scanId", "severity"]),

  findingComments: defineTable({
    findingId: v.id("findings"),
    userId: v.id("users"),
    content: v.string(),
    createdAt: v.number(),
  }).index("by_finding", ["findingId"]),

  integrations: defineTable({
    projectId: v.id("projects"),
    type: v.union(v.literal("jira"), v.literal("github")),
    config: v.any(),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_project", ["projectId"])
    .index("by_project_type", ["projectId", "type"]),

  scanProfiles: defineTable({
    ownerId: v.optional(v.id("users")),
    name: v.string(),
    description: v.optional(v.string()),
    config: v.any(),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_owner", ["ownerId"]),

  activityLogs: defineTable({
    userId: v.optional(v.id("users")),
    actionType: v.string(),
    description: v.string(),
    metadata: v.optional(v.any()),
    createdAt: v.number(),
  }).index("by_user_time", ["userId", "createdAt"]),

  systemMetrics: defineTable({
    trafficInMbps: v.optional(v.number()),
    trafficOutMbps: v.optional(v.number()),
    availabilityScore: v.optional(v.number()),
    activeScans: v.optional(v.number()),
    timestamp: v.number(),
  }).index("by_timestamp", ["timestamp"]),
});
