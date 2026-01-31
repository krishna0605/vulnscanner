s# Production Deployment Guide

This project requires a **Split Deployment** strategy because:

1.  **Frontend (`/frontend`)**: Next.js app (Perfect for Vercel).
2.  **Backend (`/backend`)**: Fastify app with **Cron Jobs** and **Playwright** (Browsers).
    - _Note: Browsers and long-running tasks are NOT supported on Vercel Serverless. You must use a Docker host like Railway, Render, or Fly.io._

---

## Part 1: Backend Deployment (Railway/Render)

**Do this FIRST**, as you will need the Backend URL for the Frontend configuration.

### Option A: Railway (Recommended)

1.  Go to [Railway.app](https://railway.app/) and create a new project.
2.  Select **"Deploy from GitHub repo"**.
3.  Select your repository: `krishna0605/vulnscanner`.
4.  **Configuration**:
    - We have added a `railway.toml` file to your repository which automatically sets the **Root Directory** to `/backend`.
    - You do **NOT** need to configure the Root Directory manually in the settings.
5.  **Environment Variables**:
    - Go to `Variables`.
    - Add the following keys (copy from your local `.env`):
      - `SUPABASE_URL`
      - `SUPABASE_SERVICE_ROLE_KEY`
      - `PORT` (Value: `3001` or let Railway assign one as `PORT`)
6.  **Deploy**:
    - If a deployment started automatically, it might have failed initially (before `railway.toml` was added).
    - Go to "Deployments" and click **Redeploy** on the latest commit (which includes `railway.toml`).
7.  Once deployed, copy the **Public Domain** provided by Railway (e.g., `https://vulnscanner-backend.up.railway.app`).
    - _Note: You might need to generate a domain in `Settings` -> `Networking`._

---

## Part 2: Frontend Deployment (Vercel)

1.  Go to [Vercel Dashboard](https://vercel.com/new).
2.  Import the repository: `krishna0605/vulnscanner`.
3.  **Project Configuration** (Critical Step):
    - **Root Directory**: Click `Edit` and select `frontend`.
    - **Framework Preset**: It should verify as `Next.js` automatically after selecting the root directory.
4.  **Environment Variables**:
    - Expand "Environment Variables".
    - Add the following:
      - `NEXT_PUBLIC_SUPABASE_URL`: (Your Supabase URL)
      - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: (Your Supabase Anon Key)
      - `BACKEND_URL`: **(The Railway URL from Part 1)**
        - _Example: `https://vulnscanner-backend.up.railway.app`_
        - _Important: Do NOT add a trailing slash `/`._
5.  **Deploy**: Click "Deploy".

---

## Part 3: Post-Deployment Verification

1.  Open your new Vercel URL.
2.  Try to log in (Supabase Auth).
3.  Test a scan.
    - If the scan fails immediately, check the **Console** (F12) for CORS errors or 404s on `/api/...`.
    - If you see CORS errors, you may need to add the Vercel Domain to the `CORS_ORIGINS` or `ALLOWED_ORIGINS` in your Backend Environment Variables on Railway.
