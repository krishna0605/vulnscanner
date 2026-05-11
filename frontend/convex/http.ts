import { httpAction } from "./_generated/server";
import { httpRouter } from "convex/server";
import { Webhook } from "svix";
import { api, internal } from "./_generated/api";

const http = httpRouter();

function requireScannerToken(request: Request) {
  const expected = process.env.SCANNER_SERVICE_TOKEN;
  const header = request.headers.get("authorization") ?? "";
  if (!expected || header !== `Bearer ${expected}`) {
    throw new Error("Unauthorized scanner request");
  }
}

http.route({
  path: "/clerk/webhook",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const secret = process.env.CLERK_WEBHOOK_SECRET;
    if (!secret) return new Response("Missing webhook secret", { status: 500 });

    const payload = await request.text();
    const wh = new Webhook(secret);
    let event: any;
    try {
      event = wh.verify(payload, {
        "svix-id": request.headers.get("svix-id") ?? "",
        "svix-timestamp": request.headers.get("svix-timestamp") ?? "",
        "svix-signature": request.headers.get("svix-signature") ?? "",
      });
    } catch {
      return new Response("Invalid webhook signature", { status: 400 });
    }

    if (event.type === "user.created" || event.type === "user.updated") {
      const user = event.data;
      const email = user.email_addresses?.find((item: any) => item.id === user.primary_email_address_id)?.email_address
        ?? user.email_addresses?.[0]?.email_address;
      await ctx.runMutation(api.users.upsertFromClerk, {
        clerkId: user.id,
        email,
        name: [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username || email,
        avatarUrl: user.image_url,
      });
    }

    if (event.type === "user.deleted" && event.data?.id) {
      await ctx.runMutation(api.users.removeFromClerk, { clerkId: event.data.id });
    }

    return new Response("ok", { status: 200 });
  }),
});

for (const route of [
  ["log", internal.scanner.addLog],
  ["progress", internal.scanner.updateProgress],
  ["asset", internal.scanner.addAsset],
  ["finding", internal.scanner.addFinding],
  ["complete", internal.scanner.completeScan],
  ["fail", internal.scanner.failScan],
  ["started", internal.scanner.markStarted],
] as const) {
  http.route({
    path: `/scanner/${route[0]}`,
    method: "POST",
    handler: httpAction(async (ctx, request) => {
      try {
        requireScannerToken(request);
        const body = await request.json();
        await ctx.runMutation(route[1] as any, body);
        return Response.json({ success: true });
      } catch (error: any) {
        return Response.json({ success: false, error: error.message }, { status: error.message === "Unauthorized scanner request" ? 401 : 400 });
      }
    }),
  });
}

http.route({
  path: "/scanner/status",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    try {
      requireScannerToken(request);
      const body = await request.json();
      const status = await ctx.runQuery(internal.scanner.status, body);
      return Response.json({ success: true, data: status });
    } catch (error: any) {
      return Response.json(
        { success: false, error: error.message },
        { status: error.message === "Unauthorized scanner request" ? 401 : 400 },
      );
    }
  }),
});

export default http;
