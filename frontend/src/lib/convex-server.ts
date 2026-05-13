import 'server-only';

import { auth } from '@clerk/nextjs/server';
import { ConvexHttpClient } from 'convex/browser';

export class ConvexAuthTokenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConvexAuthTokenError';
  }
}

export async function getConvexServerClient() {
  const url = process.env.NEXT_PUBLIC_CONVEX_URL;
  if (!url) {
    throw new Error('NEXT_PUBLIC_CONVEX_URL is not configured');
  }

  const client = new ConvexHttpClient(url);
  const { getToken } = await auth();
  const token = await getToken({ template: 'convex' }).catch((error) => {
    throw new ConvexAuthTokenError(
      `Unable to request Clerk JWT template "convex": ${error instanceof Error ? error.message : String(error)}`
    );
  });

  if (!token) {
    throw new ConvexAuthTokenError(
      'Missing Clerk JWT template "convex". Confirm the Clerk Convex integration/JWT template and matching Vercel Clerk keys.'
    );
  }

  client.setAuth(token);

  return client;
}

export async function safeConvex<T>(operation: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await operation();
  } catch {
    return fallback;
  }
}
