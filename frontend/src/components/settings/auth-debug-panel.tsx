'use client';

import { useAuth, useUser } from '@clerk/nextjs';
import { useConvexAuth, useQuery } from 'convex/react';
import { AlertTriangle, CheckCircle2, Loader2, RefreshCw, ShieldCheck } from 'lucide-react';
import { api } from '@convex/_generated/api';
import { Button } from '@/components/ui/button';

export function AuthDebugPanel() {
  const { isLoaded: clerkLoaded, isSignedIn } = useAuth();
  const { user } = useUser();
  const { isAuthenticated: convexAuthenticated, isLoading: convexLoading } = useConvexAuth();
  const identity = useQuery(api.auth.debugIdentity, {});
  const loading = !clerkLoaded || convexLoading || identity === undefined;

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-[24px] border border-white/10 p-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-cyan-300">
              <ShieldCheck className="h-3.5 w-3.5" />
              Auth Health
            </div>
            <h1 className="text-3xl font-bold text-white">Clerk + Convex diagnostics</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
              This page checks whether the browser has a Clerk session and whether Convex accepts
              that session as a valid app identity.
            </p>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={() => window.location.reload()}
            className="h-10 rounded-xl border-white/10 bg-white/5 text-white hover:bg-white/10"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Recheck
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <StatusTile
          label="Clerk session"
          loading={!clerkLoaded}
          ok={Boolean(isSignedIn)}
          detail={isSignedIn ? user?.primaryEmailAddress?.emailAddress ?? 'Signed in' : 'Not signed in'}
        />
        <StatusTile
          label="Convex provider"
          loading={convexLoading}
          ok={convexAuthenticated}
          detail={convexAuthenticated ? 'Token accepted by client provider' : 'No accepted Convex token'}
        />
        <StatusTile
          label="Convex user row"
          loading={identity === undefined}
          ok={Boolean(identity?.userRecordFound)}
          detail={identity?.userRecordFound ? 'User record found' : 'User record missing or not authenticated'}
        />
      </div>

      <div className="glass-panel rounded-[24px] border border-white/10 p-6">
        <h2 className="text-lg font-bold text-white">Convex identity payload</h2>
        <div className="mt-4 rounded-2xl border border-white/10 bg-black/30 p-4 font-mono text-xs leading-6 text-slate-300">
          {loading ? (
            <span className="inline-flex items-center text-slate-400">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Checking auth state...
            </span>
          ) : (
            <pre className="whitespace-pre-wrap break-words">
              {JSON.stringify(
                {
                  clerkLoaded,
                  clerkSignedIn: Boolean(isSignedIn),
                  convexClientAuthenticated: convexAuthenticated,
                  convexIdentityAuthenticated: identity?.isAuthenticated ?? false,
                  convexUserRecordFound: identity?.userRecordFound ?? false,
                  issuer: identity?.issuer ?? null,
                  subject: identity?.subject ?? null,
                  email: identity?.email ?? null,
                },
                null,
                2
              )}
            </pre>
          )}
        </div>
      </div>

      {!loading && (!convexAuthenticated || !identity?.isAuthenticated || !identity?.userRecordFound) && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-5 text-sm leading-6 text-amber-100">
          Convex auth is not fully healthy yet. Confirm the Clerk JWT template named
          <span className="font-mono"> convex</span>, the Convex
          <span className="font-mono"> CLERK_JWT_ISSUER_DOMAIN</span>, and matching Vercel Clerk
          keys, then sign out and sign in again.
        </div>
      )}
    </div>
  );
}

function StatusTile({
  label,
  loading,
  ok,
  detail,
}: {
  label: string;
  loading: boolean;
  ok: boolean;
  detail: string;
}) {
  const Icon = loading ? Loader2 : ok ? CheckCircle2 : AlertTriangle;

  return (
    <div className="glass-panel rounded-[20px] border border-white/10 p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-slate-500">{label}</p>
          <p className="mt-2 text-sm text-slate-300">{detail}</p>
        </div>
        <span
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${
            loading
              ? 'border-slate-500/20 bg-slate-500/10 text-slate-300'
              : ok
                ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300'
                : 'border-amber-500/20 bg-amber-500/10 text-amber-300'
          }`}
        >
          <Icon className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
        </span>
      </div>
    </div>
  );
}
