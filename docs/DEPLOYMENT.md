# Deployment Guide

VulnScanner uses a split deployment:

| Area | Platform | Responsibility |
| --- | --- | --- |
| Frontend | Vercel | Next.js UI and server actions |
| Auth | Clerk | Sign-in, sign-up, sessions, user identity |
| Data/backend functions | Convex | DB, realtime queries, mutations, scanner writebacks |
| Scanner runtime | Railway | Playwright crawling and long-running scan jobs |
| AI enrichment | Hugging Face | Optional model/API calls |

## Vercel

Set the project root to `frontend`.

Required variables:

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

## Convex

Deploy from `frontend`:

```bash
cd frontend
npx convex deploy
```

Required variables:

```env
CLERK_JWT_ISSUER_DOMAIN=https://your-clerk-domain.clerk.accounts.dev
CLERK_WEBHOOK_SECRET=whsec_...
RAILWAY_BACKEND_URL=https://your-railway-service.up.railway.app
SCANNER_SERVICE_TOKEN=replace-with-a-long-random-shared-secret
```

## Railway

Deploy the `backend` directory.

Required variables:

```env
CONVEX_SITE_URL=https://your-convex-deployment.convex.site
SCANNER_SERVICE_TOKEN=replace-with-the-same-secret-used-in-convex
NODE_ENV=production
PORT=3001
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW_MS=60000
```

Optional variables:

```env
SENTRY_DSN=https://your-dsn@sentry.io/project-id
HUGGINGFACE_API_TOKEN=hf_...
```

## Health Checks

| Service | Endpoint |
| --- | --- |
| Frontend | `/api/health` |
| Backend | `/health` |

## Rollback

- Vercel: redeploy a previous frontend deployment.
- Railway: redeploy a previous backend deployment.
- Convex: redeploy the previous code revision if schema/function changes need to be rolled back.
