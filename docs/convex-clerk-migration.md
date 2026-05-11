# Convex + Clerk Migration

This project is being migrated from Supabase Auth/Postgres/Realtime to Clerk + Convex.

## Target Ownership

- Clerk owns authentication, sessions, OAuth, profile identity, and auth UI.
- Convex owns application data, realtime reads, mutations, scan state, logs, findings, comments, reports, integrations, and activity.
- Railway owns Playwright scanning and writes status/results back to Convex through Convex HTTP actions.
- Hugging Face remains optional and should initially be called from Railway when scan enrichment needs long-running work.
- Supabase remains only as a temporary migration/backout dependency until the cutover is verified.

## Local Setup

From `frontend`:

```bash
npm install
npx convex dev
```

Create or select a Convex project when prompted. Convex will generate `frontend/convex/_generated` and local Convex env entries.

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
2. Enable email/password and Google OAuth.
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

## Migration Sequence

1. Rotate old Supabase database credentials before migration.
2. Create Clerk and Convex dev/prod apps.
3. Add Convex dashboard variables.
4. Add Vercel variables.
5. Add Railway variables.
6. Run `npx convex dev` to generate Convex client/server files.
7. Test Clerk sign-in, Clerk webhook user sync, project creation, scan dispatch, scanner progress, findings, comments, and reports in dev.
8. Export Supabase tables and import compact records into Convex using `legacySupabaseId` fields for mapping.
9. Keep Supabase read-only for 7-14 days.
10. Remove Supabase env vars, archived debug scripts, and legacy compatibility routes once production reports match.

## Free-Tier Guardrails

- Do not store raw HTML, screenshots, response bodies, or large headers in Convex.
- Truncate scan logs and finding evidence.
- Keep Playwright on Railway, not Convex actions.
- Use Convex realtime queries for UI state instead of polling Railway.
