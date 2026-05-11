import Link from 'next/link';
import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-background-dark text-slate-200 px-4">
      <Link href="/" className="mb-8 flex items-center text-white font-bold text-xl">
        <span className="material-symbols-outlined mr-2">shield</span>
        Vuln<span className="text-slate-400">Scanner</span>
      </Link>
      <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" afterSignUpUrl="/dashboard" />
    </main>
  );
}
