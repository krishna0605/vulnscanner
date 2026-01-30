# Database Configuration & Connection Pooling

## Connection Settings

Supabase uses **PgBouncer** for connection pooling. This is critical for serverless environments (like Next.js API routes) to prevent exhausting database connections.

### Connection Limits

| Plan | Connection Limit | Pool Limit (Transaction) | Pool Limit (Session) |
| ---- | ---------------- | ------------------------ | -------------------- |
| Free | 20 (Direct)      | 60                       | 20                   |
| Pro  | 60 (Direct)      | 60+ (Configurable)       | 60+                  |

### Best Practices

1. **Use Transaction Mode (Port 6543)**
   - Recommended for Fastify backend and Next.js SSR
   - Connection is returned to pool immediately after transaction/query
   - **Environment Variable**: `DATABASE_URL` should point to port 6543

2. **Use Session Mode (Port 5432)**
   - Use only for long-running processes (e.g., migrations, heavy analytics)
   - Keeps connection open until client disconnects

## Connection Pooling Implementation

The application does not need a local pooler (like `pg-pool`) because Supabase handles this infrastructure.

### Prisma Configuration (if applicable)

If using Prisma, ensure `pgbouncer=true` is appended to the connection string:

```env
DATABASE_URL="postgres://user:pass@host:6543/db?pgbouncer=true"
```

### Fastify / Node.js Clients

When using `postgres.js` or `node-postgres`, set a conservative `max` connection count per instance:

```typescript
const sql = postgres(process.env.DATABASE_URL, {
  max: 5, // Keep low per container/lambda
  idle_timeout: 20,
});
```

## Troubleshooting

- **"remaining connection slots are reserved used for non-replication superuser"**
  - **Cause**: Too many direct connections.
  - **Fix**: Switch `DATABASE_URL` to use the pooler port (6543).

- **"prepared statement "s1" already exists"**
  - **Cause**: Using prepared statements in Transaction Mode.
  - **Fix**: Disable prepared statements in your ORM/client or switch to Session Mode.

## Validating Connections

Use the `pg_stat_activity` view to monitor active connections:

```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```
