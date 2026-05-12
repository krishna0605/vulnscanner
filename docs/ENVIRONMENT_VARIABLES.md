# Environment Variables

This document lists the active environment variables for the Convex + Clerk + Railway stack.

## Frontend / Vercel

| Variable | Required | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_CONVEX_URL` | Yes | Convex client URL, ending in `.convex.cloud` |
| `NEXT_PUBLIC_CONVEX_SITE_URL` | Recommended | Convex HTTP actions URL, ending in `.convex.site` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk public browser key |
| `CLERK_SECRET_KEY` | Yes | Clerk server key |
| `CLERK_WEBHOOK_SECRET` | Yes | Clerk webhook signing secret |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | Yes | Usually `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | Yes | Usually `/sign-up` |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` | Yes | Usually `/dashboard` |
| `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL` | Yes | Usually `/dashboard` |
| `BACKEND_URL` | Yes | Railway scanner backend URL |
| `NEXT_PUBLIC_SENTRY_DSN` | Optional | Browser Sentry DSN |

## Convex

| Variable | Required | Description |
| --- | --- | --- |
| `CLERK_JWT_ISSUER_DOMAIN` | Yes | Clerk issuer domain for Convex auth |
| `CLERK_WEBHOOK_SECRET` | Yes | Clerk webhook signing secret |
| `RAILWAY_BACKEND_URL` | Yes | Railway scanner backend URL |
| `SCANNER_SERVICE_TOKEN` | Yes | Shared secret between Convex and Railway |
| `HUGGINGFACE_API_TOKEN` | Optional | Use only if Convex calls Hugging Face directly |

## Backend / Railway

| Variable | Required | Description |
| --- | --- | --- |
| `CONVEX_SITE_URL` | Yes | Convex HTTP actions URL |
| `SCANNER_SERVICE_TOKEN` | Yes | Same shared secret configured in Convex |
| `PORT` | Recommended | Railway usually provides this; local default is `3001` |
| `NODE_ENV` | Recommended | `production`, `development`, or `test` |
| `ALLOWED_ORIGINS` | Yes | Comma-separated Vercel/custom domains |
| `RATE_LIMIT_MAX` | Recommended | Default request limit |
| `RATE_LIMIT_WINDOW_MS` | Recommended | Rate-limit window in milliseconds |
| `SENTRY_DSN` | Optional | Backend Sentry DSN |
| `HUGGINGFACE_API_TOKEN` | Optional | AI enrichment token |

## Local Development

Copy the examples and fill in local or development values:

```bash
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

## Security Notes

- Do not commit real `CLERK_SECRET_KEY`, `CLERK_WEBHOOK_SECRET`, `SCANNER_SERVICE_TOKEN`, Sentry DSNs, or Hugging Face tokens.
- `NEXT_PUBLIC_*` variables are visible to browsers, so only put public values there.
- Rotate any key that was pasted into chat, logs, screenshots, or commit history.
