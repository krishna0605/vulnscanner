# Database Configuration

VulnScanner uses Convex as the application database and realtime backend.

## Data Ownership

| Data | Owner |
| --- | --- |
| Users and identity mirror | Clerk + Convex `users` table |
| Projects | Convex |
| Scans, logs, assets, and findings | Convex |
| Reports and dashboard summaries | Convex queries |
| Browser automation runtime | Railway scanner backend |

## Storage Rules

- Store compact scan state, structured findings, target URLs, scores, and short logs in Convex.
- Do not store raw page HTML, screenshots, large response bodies, or bulky crawl metadata in Convex.
- Keep long-running Playwright work inside Railway and write only normalized results back to Convex.

## Local Development

Run Convex from the frontend workspace:

```bash
cd frontend
npx convex dev
```

Deploy production Convex functions separately:

```bash
cd frontend
npx convex deploy
```

## Operational Checks

- Confirm Clerk webhooks create or update Convex users.
- Confirm scan lifecycle events are written through Convex HTTP actions.
- Watch Convex dashboard storage usage and keep free-tier data compact.
