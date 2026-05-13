'use client';

import { useEffect, useMemo, useRef } from 'react';
import { useAuth } from '@clerk/nextjs';
import { ConvexProviderWithClerk } from 'convex/react-clerk';
import { ConvexReactClient, useConvexAuth, useMutation } from 'convex/react';
import { api } from '@convex/_generated/api';
import { logger } from '@/utils/logger';

export function ConvexClientProvider({ children }: { children: React.ReactNode }) {
  const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL;
  const convex = useMemo(() => {
    return convexUrl ? new ConvexReactClient(convexUrl) : null;
  }, [convexUrl]);

  if (!convex) {
    return <>{children}</>;
  }

  return (
    <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
      <ConvexUserSync />
      {children}
    </ConvexProviderWithClerk>
  );
}

function ConvexUserSync() {
  const { isAuthenticated } = useConvexAuth();
  const syncCurrent = useMutation(api.users.syncCurrent);
  const hasSynced = useRef(false);

  useEffect(() => {
    if (!isAuthenticated || hasSynced.current) return;
    hasSynced.current = true;
    void syncCurrent({}).catch((error) => {
      hasSynced.current = false;
      logger.error('Failed to sync Clerk user into Convex', { error });
    });
  }, [isAuthenticated, syncCurrent]);

  return null;
}
