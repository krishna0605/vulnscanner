import { AuthDebugPanel } from '@/components/settings/auth-debug-panel';

export const dynamic = 'force-dynamic';

export default function AuthDebugPage() {
  return (
    <div className="mx-auto max-w-[1200px] pb-20">
      <AuthDebugPanel />
    </div>
  );
}
