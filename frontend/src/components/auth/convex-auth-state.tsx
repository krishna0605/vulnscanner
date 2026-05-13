'use client';

import Link from 'next/link';
import { Loader2, RefreshCw, ShieldAlert } from 'lucide-react';
import { useConvexAuth } from 'convex/react';
import { Button } from '@/components/ui/button';

interface ConvexAuthStateProps {
  title: string;
  message: string;
  variant?: 'loading' | 'error';
}

export function ConvexAuthState({ title, message, variant = 'loading' }: ConvexAuthStateProps) {
  const Icon = variant === 'loading' ? Loader2 : ShieldAlert;

  return (
    <div className="glass-panel rounded-[24px] border border-white/10 p-8">
      <div className="flex items-start gap-4">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-cyan-300">
          <Icon className={`h-5 w-5 ${variant === 'loading' ? 'animate-spin' : ''}`} />
        </span>
        <div className="space-y-3">
          <div>
            <h2 className="text-xl font-bold text-white">{title}</h2>
            <p className="mt-1 text-sm leading-6 text-slate-400">{message}</p>
          </div>
          {variant === 'error' && (
            <div className="flex flex-wrap gap-3">
              <Button asChild className="h-10 rounded-xl bg-white px-4 text-sm font-bold text-black hover:bg-slate-200">
                <Link href="/sign-in">Sign in again</Link>
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => window.location.reload()}
                className="h-10 rounded-xl border-white/10 bg-white/5 px-4 text-sm text-white hover:bg-white/10"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Retry
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function ConvexAuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useConvexAuth();

  if (isLoading) {
    return (
      <ConvexAuthState
        title="Authenticating workspace..."
        message="Connecting your Clerk session to Convex before loading workspace data."
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ConvexAuthState
        title="Session needs refresh"
        message="Clerk is signed in, but Convex has not accepted an auth token for this session yet. Refresh the session after confirming the Clerk Convex JWT template and Convex issuer."
        variant="error"
      />
    );
  }

  return <>{children}</>;
}
