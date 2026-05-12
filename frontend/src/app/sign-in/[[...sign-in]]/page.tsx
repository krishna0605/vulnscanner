import Link from 'next/link';
import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  const skipAuthForE2E = process.env.E2E_SKIP_AUTH === 'true';

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-background-dark text-slate-200 px-4">
      <Link href="/" className="mb-8 flex items-center text-white font-bold text-xl">
        <span className="material-symbols-outlined mr-2">shield</span>
        Vuln<span className="text-slate-400">Scanner</span>
      </Link>
      {skipAuthForE2E ? (
        <section className="rounded-lg border border-slate-700 bg-slate-900 p-8 text-center">
          <h1 className="text-2xl font-semibold text-white">Sign in to VulnScanner</h1>
          <p className="mt-3 text-slate-400">Authentication is disabled for E2E test mode.</p>
        </section>
      ) : (
        <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" afterSignInUrl="/dashboard" />
      )}
    </main>
  );
}
