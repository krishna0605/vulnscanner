# Environment Variables Documentation

This document describes all environment variables used by the VulnScanner application.

---

## Backend Environment Variables

Set these in `backend/.env` for local development or in your hosting platform's environment configuration for production.

### Required Variables

| Variable                    | Description                     | Example                      |
| --------------------------- | ------------------------------- | ---------------------------- |
| `SUPABASE_URL`              | Your Supabase project URL       | `https://abc123.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (admin access) | `eyJhbGciOiJIUzI1NiIs...`    |

### Optional Variables

| Variable               | Default       | Description                                                        |
| ---------------------- | ------------- | ------------------------------------------------------------------ |
| `PORT`                 | `3001`        | Server port                                                        |
| `NODE_ENV`             | `development` | Environment: `development`, `production`, or `test`                |
| `LOG_LEVEL`            | `info`        | Pino log level: `fatal`, `error`, `warn`, `info`, `debug`, `trace` |
| `DATABASE_URL`         | -             | Direct PostgreSQL connection URL (for migrations)                  |
| `ALLOWED_ORIGINS`      | localhost     | Comma-separated list of allowed CORS origins                       |
| `RATE_LIMIT_MAX`       | `100`         | Maximum requests per time window                                   |
| `RATE_LIMIT_WINDOW_MS` | `60000`       | Rate limit window in milliseconds                                  |
| `SENTRY_DSN`           | -             | Sentry error tracking DSN                                          |

---

## Frontend Environment Variables

Set these in `frontend/.env.local` for local development or in Vercel/hosting platform for production.

### Required Variables

| Variable                        | Description                     | Example                      |
| ------------------------------- | ------------------------------- | ---------------------------- |
| `NEXT_PUBLIC_SUPABASE_URL`      | Supabase project URL (public)   | `https://abc123.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key (public) | `eyJhbGciOiJIUzI1NiIs...`    |

### Optional Variables

| Variable                 | Default                 | Description                                        |
| ------------------------ | ----------------------- | -------------------------------------------------- |
| `BACKEND_URL`            | `http://localhost:3001` | Backend API URL (used in next.config.mjs rewrites) |
| `NEXT_PUBLIC_SENTRY_DSN` | -                       | Sentry error tracking DSN (public)                 |

---

## Setting Up Environment Variables

### Local Development

1. Copy the example files:

   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend
   cp frontend/.env.example frontend/.env.local
   ```

2. Fill in your Supabase credentials from your Supabase dashboard.

### Production Deployment

#### Vercel (Frontend)

1. Go to Project Settings > Environment Variables
2. Add each variable with appropriate scope (Production, Preview, Development)

#### Railway (Backend)

1. Go to Service > Variables
2. Add variables via the UI or use Railway CLI

#### Docker / Other Platforms

Pass environment variables via:

- Docker: `-e` flags or `.env` file
- Kubernetes: ConfigMaps / Secrets
- Fly.io: `fly secrets set`

---

## Security Notes

> [!CAUTION]
> **Never commit real credentials to version control!**

- `SUPABASE_SERVICE_ROLE_KEY` has **full admin access** - keep it secret
- `NEXT_PUBLIC_*` variables are exposed to the browser - only use for public keys
- Use secrets management (Vault, AWS Secrets Manager) for production credentials
