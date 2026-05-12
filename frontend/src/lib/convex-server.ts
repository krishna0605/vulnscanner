import 'server-only';

import { auth } from '@clerk/nextjs/server';
import { ConvexHttpClient } from 'convex/browser';

export async function getConvexServerClient() {
  const url = process.env.NEXT_PUBLIC_CONVEX_URL;
  if (!url) {
    throw new Error('NEXT_PUBLIC_CONVEX_URL is not configured');
  }

  const client = new ConvexHttpClient(url);
  const { getToken } = await auth();
  const token = await getToken({ template: 'convex' }).catch(() => null);

  if (token) {
    client.setAuth(token);
  }

  return client;
}

export async function safeConvex<T>(operation: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await operation();
  } catch {
    return fallback;
  }
}
