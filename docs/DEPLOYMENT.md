# Deployment Guide

This document covers deploying VulnScanner to production environments.

## Deployment Options

| Option               | Frontend  | Backend   | Complexity |
| -------------------- | --------- | --------- | ---------- |
| **Vercel + Railway** | Vercel    | Railway   | Low        |
| **Docker Compose**   | Container | Container | Medium     |
| **Kubernetes**       | K8s       | K8s       | High       |

---

## Option 1: Vercel + Railway (Recommended)

### Frontend (Vercel)

1. **Connect Repository**

   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Deploy from frontend directory
   cd frontend
   vercel
   ```

2. **Configure Environment Variables** in Vercel Dashboard:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `BACKEND_URL` (Railway URL)

### Backend (Railway)

1. **Connect Repository** via Railway Dashboard
2. **Set Root Directory** to `backend`
3. **Configure Environment Variables**:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `ALLOWED_ORIGINS` (Vercel URL)
   - `PORT=3001`

---

## Option 2: Docker Compose

### Prerequisites

- Docker & Docker Compose installed
- Environment variables configured

### Deploy

```bash
# Create .env file from example
cp backend/.env.example .env

# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

---

## Health Checks

Both services expose health endpoints:

| Service  | Endpoint      | Expected Response            |
| -------- | ------------- | ---------------------------- |
| Frontend | `/api/health` | `{ status: 'ok' }`           |
| Backend  | `/health`     | `{ status: 'healthy', ... }` |

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) handles:

1. **Lint & Type Check** - Code quality
2. **Unit Tests** - Backend/Frontend tests
3. **Build** - Compile TypeScript, Next.js build
4. **Docker Build** - Container image creation (on main branch)

---

## Rollback Procedure

### Vercel

```bash
vercel rollback [deployment-url]
```

### Railway

Use Railway dashboard to redeploy previous commit.

### Docker

```bash
# Tag previous working image
docker tag vulnscanner-backend:latest vulnscanner-backend:rollback

# Rollback
docker-compose down
docker tag vulnscanner-backend:rollback vulnscanner-backend:latest
docker-compose up -d
```

---

## Monitoring & Observability

| Tool               | Purpose           | Integration        |
| ------------------ | ----------------- | ------------------ |
| Sentry             | Error Tracking    | Already configured |
| Supabase Dashboard | DB Metrics        | Built-in           |
| Docker Stats       | Container Metrics | `docker stats`     |

---

## Security Checklist

- [ ] Environment variables set (not hardcoded)
- [ ] CORS configured for production domains only
- [ ] Rate limiting enabled
- [ ] HTTPS enforced (Vercel/Railway handle this)
- [ ] Non-root container users
- [ ] Health checks configured
