'use client';

import * as Sentry from '@sentry/nextjs';
import { useEffect } from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body>
        <div className="flex min-h-screen flex-col items-center justify-center bg-black text-white p-4">
          <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
          <p className="text-slate-400 mb-6">A critical error occurred.</p>
          <button
            onClick={() => reset()}
            className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-500 transition-colors"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
