'use client';

import Link from 'next/link';
import { login } from '../actions';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleButton } from '@/components/auth/google-button';


export default function LoginPage() {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(formData: FormData) {
    setLoading(true);
    setError(null);

    const result = await login(formData);

    if (result?.error) {
      setError(result.error);
      setLoading(false);
    } else {
      // Redirect is handled in server action, but just in case
      // router.push('/dashboard');
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-background-dark text-slate-200 font-sans overflow-x-hidden relative selection:bg-white selection:text-black">
      {/* Background Elements */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-stealth-gradient opacity-80"></div>
      <div className="fixed top-[-10%] left-[-10%] w-[800px] h-[800px] bg-white/5 rounded-full blur-[150px] animate-pulse pointer-events-none"></div>
      <div
        className="fixed bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-gray-500/10 rounded-full blur-[150px] animate-pulse pointer-events-none"
        style={{ animationDelay: '2s' }}
      ></div>

      <nav className="absolute top-0 w-full z-50 pt-6 px-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="flex items-center cursor-pointer group">
            <div className="relative w-8 h-8 mr-3 flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-2xl absolute">shield</span>
              <div className="absolute inset-0 bg-white/10 blur-md rounded-full group-hover:bg-white/20 transition-all"></div>
            </div>
            <span className="font-sans font-bold text-lg tracking-tight text-white group-hover:text-slate-200 transition-colors">
              Vuln<span className="text-slate-400">Scanner</span>
            </span>
          </Link>
          <Link
            href="/"
            className="text-slate-400 hover:text-white text-sm font-mono transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            Back to Home
          </Link>
        </div>
      </nav>

      <div className="flex-grow flex items-center justify-center px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="w-full max-w-md">
          <div className="glass-panel login-glass rounded-[24px] p-8 sm:p-10 relative overflow-hidden backdrop-blur-xl border border-white/10 shadow-2xl bg-white/5">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-white/5 border border-white/10 mb-4 shadow-glow">
                <span className="material-symbols-outlined text-white">lock</span>
              </div>
              <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">Welcome Back</h2>
              <p className="text-slate-400 text-sm font-light">
                Enter your credentials to access the console.
              </p>
            </div>

            <form action={handleSubmit} className="space-y-6">
              {error && (
                <div className="bg-red-500/10 border border-red-500/50 text-red-500 text-sm p-3 rounded-lg text-center">
                  {error}
                </div>
              )}

              <div>
                <label
                  className="block text-xs font-mono font-medium text-slate-300 mb-2 uppercase tracking-wider"
                  htmlFor="email"
                >
                  Work Email
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="material-symbols-outlined text-slate-500 group-focus-within:text-white transition-colors text-lg">
                      mail
                    </span>
                  </div>
                  <input
                    autoComplete="email"
                    className="form-input block w-full pl-10 pr-3 py-3 rounded-lg text-sm placeholder-slate-500 focus:shadow-input-glow bg-white/5 border border-white/10 text-white focus:bg-white/10 focus:border-white/30 outline-none transition-all"
                    id="email"
                    name="email"
                    placeholder="name@company.com"
                    required
                    type="email"
                  />
                </div>
              </div>
              <div>
                <label
                  className="block text-xs font-mono font-medium text-slate-300 mb-2 uppercase tracking-wider"
                  htmlFor="password"
                >
                  Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="material-symbols-outlined text-slate-500 group-focus-within:text-white transition-colors text-lg">
                      key
                    </span>
                  </div>
                  <input
                    autoComplete="current-password"
                    className="form-input block w-full pl-10 pr-3 py-3 rounded-lg text-sm placeholder-slate-500 focus:shadow-input-glow bg-white/5 border border-white/10 text-white focus:bg-white/10 focus:border-white/30 outline-none transition-all"
                    id="password"
                    name="password"
                    placeholder="••••••••"
                    required
                    type="password"
                  />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    className="h-4 w-4 rounded bg-white/5 border-white/20 text-white focus:ring-offset-0 focus:ring-1 focus:ring-white/50 checkbox-custom transition-all cursor-pointer"
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                  />
                  <label
                    className="ml-2 block text-sm text-slate-400 hover:text-slate-300 cursor-pointer select-none"
                    htmlFor="remember-me"
                  >
                    Remember me
                  </label>
                </div>
                <div className="text-sm">
                  <Link
                    className="font-medium text-slate-400 hover:text-white transition-colors"
                    href="/forgot-password"
                  >
                    Forgot password?
                  </Link>
                </div>
              </div>
              <div>
                <button
                  className="w-full flex justify-center py-3 px-4 rounded-lg text-sm font-bold text-black bg-white hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#313131] focus:ring-white transition-all transform hover:-translate-y-0.5 shadow-glow hover:shadow-glow-hover disabled:opacity-50 disabled:cursor-not-allowed"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? 'LOGGING IN...' : 'LOG IN'}
                </button>
              </div>
            </form>

            {/* Divider */}
            <div className="mt-6 flex items-center">
              <div className="flex-grow border-t border-white/10"></div>
              <span className="px-4 text-xs text-slate-500 font-mono uppercase tracking-wider">or</span>
              <div className="flex-grow border-t border-white/10"></div>
            </div>

            {/* Google OAuth Button */}
            <div className="mt-6">
              <GoogleButton />
            </div>

            <div className="mt-8 pt-6 border-t border-white/5 text-center">
              <p className="text-sm text-slate-500">
                Don&apos;t have an account?
                <Link
                  className="font-medium text-white hover:text-slate-300 transition-colors ml-1"
                  href="/signup"
                >
                  Create Account
                </Link>
              </p>
            </div>
          </div>
          <div className="mt-8 flex justify-center space-x-6 text-xs text-slate-500 font-mono">
            <Link className="hover:text-slate-300 transition-colors" href="#">
              Privacy
            </Link>
            <span className="text-slate-700">|</span>
            <Link className="hover:text-slate-300 transition-colors" href="#">
              Terms
            </Link>
            <span className="text-slate-700">|</span>
            <Link className="hover:text-slate-300 transition-colors" href="#">
              Help
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
