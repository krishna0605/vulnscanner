import Link from 'next/link';
import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-background-dark text-slate-200 px-4">
      <Link href="/" className="mb-8 flex items-center text-white font-bold text-xl">
        <span className="material-symbols-outlined mr-2">shield</span>
        Vuln<span className="text-slate-400">Scanner</span>
      </Link>
      <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" afterSignInUrl="/dashboard" />
    </main>
  );
}
