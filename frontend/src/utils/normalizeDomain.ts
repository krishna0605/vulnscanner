export function normalizeDomain(input: string): string {
  const raw = (input || '').trim();
  if (!raw) return raw;
  try {
    const hasProtocol = raw.includes('://');
    const url = new URL(hasProtocol ? raw : `http://${raw}`);
    const host = url.hostname.toLowerCase();
    return host;
  } catch {
    // Fallback: strip credentials, path, port
    const host = raw.split('@').pop()?.split('/')[0]?.split(':')[0]?.toLowerCase() || raw;
    return host;
  }
}

export default normalizeDomain;