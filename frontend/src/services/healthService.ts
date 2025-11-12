import { API_BASE_URL } from './httpClient.ts';
import axios, { AxiosError } from 'axios';

/**
 * Concurrent, tolerant health check:
 * - Fires multiple endpoint probes in parallel and succeeds if any return 200.
 * - Handles net::ERR_ABORTED / request cancellations gracefully.
 * - Performs up to 2 passes with small backoff to smooth transient issues.
 */
export async function checkBackendHealth(): Promise<boolean> {
  const urls = [
    // Primary API v1 base
    `${API_BASE_URL.replace(/\/$/, '')}/health`,
    // Absolute IPv4 variant (v1)
    'http://127.0.0.1:8000/api/v1/health',
    // Non-versioned fallback (some dev builds expose this)
    'http://127.0.0.1:8000/api/health'
  ];

  const probe = async (): Promise<boolean> => {
    try {
      // Run all probes concurrently; resolve true on any 200 status
      const results = await Promise.all(
        urls.map((u) =>
          axios
            .get(u, { timeout: 4000 })
            .then((res) => res.status === 200)
            .catch((err: AxiosError) => {
              // Treat aborted/cancelled requests as transient and simply return false for this probe
              const msg = (err.message || '').toLowerCase();
              if (msg.includes('aborted') || err.code === 'ERR_CANCELED') {
                return false;
              }
              return false;
            })
        )
      );
      return results.some(Boolean);
    } catch {
      return false;
    }
  };

  for (let pass = 0; pass < 2; pass++) {
    const ok = await probe();
    if (ok) return true;
    // Small backoff between passes
    await new Promise((r) => setTimeout(r, 250));
  }

  console.warn('Backend health check failed after parallel probes.');
  return false;
}

export default { checkBackendHealth };