# Production Deployment Guide

VulnScanner now runs on:

- Vercel for the Next.js frontend
- Clerk for authentication
- Convex for application data, realtime queries, mutations, and scanner writebacks
- Railway for the Playwright scanner backend
- Hugging Face as an optional AI enrichment service

## 1. Convex

Deploy Convex from the frontend workspace:

```bash
cd frontend
npx convex deploy
```

Set these variables in the Convex dashboard:

```env
CLERK_JWT_ISSUER_DOMAIN=https://your-clerk-domain.clerk.accounts.dev
CLERK_WEBHOOK_SECRET=whsec_...
RAILWAY_BACKEND_URL=https://your-railway-service.up.railway.app
SCANNER_SERVICE_TOKEN=replace-with-a-long-random-shared-secret
```

Optional:

```env
HUGGINGFACE_API_TOKEN=hf_...
```

## 2. Railway Backend

Deploy the `backend` service to Railway. The repository contains `railway.toml`, so Railway should use the backend root automatically.

Set these Railway variables:

```env
CONVEX_SITE_URL=https://your-convex-deployment.convex.site
SCANNER_SERVICE_TOKEN=replace-with-the-same-secret-used-in-convex
NODE_ENV=production
PORT=3001
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,https://your-custom-domain.com
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=60000
SENTRY_DSN=optional
HUGGINGFACE_API_TOKEN=optional
```

After deploy, copy the Railway public domain and put it into `RAILWAY_BACKEND_URL` in Convex.

## 3. Vercel Frontend

Import the repository in Vercel and set the root directory to `frontend`.

Set these Vercel variables:

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
NEXT_PUBLIC_SENTRY_DSN=optional
```

## 4. Clerk

In Clerk:

- Enable email/password plus any social providers you want.
- Configure sign-in path as `/sign-in`.
- Configure sign-up path as `/sign-up`.
- Configure after sign-in and after sign-up paths as `/dashboard`.
- Create the Convex JWT template/integration.
- Create a webhook pointing at the Convex HTTP actions URL and use the resulting secret as `CLERK_WEBHOOK_SECRET`.

## 5. Verification

After all deployments:

1. Sign in through Clerk.
2. Create a project.
3. Start a scan.
4. Confirm Railway receives the scan request.
5. Confirm Convex receives scan logs, assets, findings, and completion status.
6. Confirm the dashboard updates without a refresh.
