# Convex + Clerk Architecture

This project now uses Clerk + Convex as the active auth and data platform.

## Ownership

- Clerk owns authentication, sessions, OAuth, profile identity, and auth UI.
- Convex owns application data, realtime reads, mutations, scan state, logs, findings, comments, reports, integrations, and activity.
- Railway owns Playwright scanning and writes status/results back to Convex through Convex HTTP actions.
- Hugging Face remains optional and should be called from Railway when scan enrichment needs long-running work.

## Local Setup

From `frontend`:

```bash
npm install
npx convex dev
```

From `backend`:

```bash
npm install
npm run dev
```

Set the same `SCANNER_SERVICE_TOKEN` in Convex and Railway/backend. The frontend dispatches a scan through the Convex `scans.start` action, Convex calls Railway `POST /scanner/run`, and Railway writes back to Convex site endpoints such as `/scanner/progress`, `/scanner/finding`, and `/scanner/complete`.

## Required Variables

Vercel/frontend:

```env
NEXT_PUBLIC_CONVEX_URL=https://your-convex-deployment.convex.cloud
NEXT_PUBLIC_CONVEX_SITE_URL=https://your-convex-deployment.convex.site
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
CLERK_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
BACKEND_URL=https://your-railway-service.up.railway.app
```

Convex dashboard:

```env
CLERK_JWT_ISSUER_DOMAIN=https://your-clerk-domain.clerk.accounts.dev
CLERK_WEBHOOK_SECRET=whsec_...
RAILWAY_BACKEND_URL=https://your-railway-service.up.railway.app
SCANNER_SERVICE_TOKEN=long-random-shared-secret
```

Railway/backend:

```env
CONVEX_SITE_URL=https://your-convex-deployment.convex.site
SCANNER_SERVICE_TOKEN=long-random-shared-secret
NODE_ENV=production
PORT=3001
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,https://your-custom-domain.com
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=60000
```

Optional:

```env
HUGGINGFACE_API_TOKEN=hf_...
SENTRY_DSN=https://...
NEXT_PUBLIC_SENTRY_DSN=https://...
```

## Clerk Setup

1. Create development and production Clerk apps.
2. Enable email/password and any social providers you need.
3. Set sign-in URL to `/sign-in`.
4. Set sign-up URL to `/sign-up`.
5. Set after sign-in and after sign-up URLs to `/dashboard`.
6. Configure the Convex integration and copy the issuer domain into `CLERK_JWT_ISSUER_DOMAIN`.
7. Add a Clerk webhook pointing to `https://your-convex-deployment.convex.site/clerk/webhook`.
8. Enable at least `user.created`, `user.updated`, and `user.deleted` webhook events.

## Convex Deployment

From `frontend`:

```bash
npx convex deploy
```

Deploy Convex before deploying Vercel/Railway production so generated functions and HTTP endpoints exist.

## Validation Sequence

1. Confirm Clerk sign-in reaches `/dashboard`.
2. Confirm Clerk webhook user sync writes to Convex.
3. Confirm project creation writes to Convex.
4. Confirm scan dispatch creates a queued scan in Convex.
5. Confirm Railway receives the scanner job.
6. Confirm Railway writes progress, logs, assets, findings, and completion back to Convex.
7. Confirm reports and dashboards read from Convex.

## Free-Tier Guardrails

- Do not store raw HTML, screenshots, response bodies, or large headers in Convex.
- Truncate scan logs and finding evidence.
- Keep Playwright on Railway, not Convex actions.
- Use Convex realtime queries for UI state instead of polling Railway.
