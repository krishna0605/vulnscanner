'use client';

import Link from 'next/link';
import { signup } from '../actions';
import { useState } from 'react';

export default function SignupPage() {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(formData: FormData) {
    setLoading(true);
    setError(null);

    // Check if passwords match if you had a confirm password field,
    // but the design only has one password field.

    const result = await signup(formData);

    if (result?.error) {
      setError(result.error);
      setLoading(false);
    }
    // Redirect handled by server action
  }

  return (
    <div className="min-h-screen flex flex-col bg-background-dark text-slate-200 font-sans overflow-x-hidden relative selection:bg-white selection:text-black">
      {/* Background Elements */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-stealth-gradient opacity-80"></div>
      <div className="fixed top-[-20%] left-[-10%] w-[600px] h-[600px] bg-white/5 rounded-full blur-[120px] animate-drift"></div>
      <div
        className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-gray-500/10 rounded-full blur-[120px] animate-drift"
        style={{ animationDelay: '-5s' }}
      ></div>

      <nav className="absolute w-full z-50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-24">
            <Link href="/" className="flex-shrink-0 flex items-center cursor-pointer group">
              <div className="relative w-10 h-10 mr-3 flex items-center justify-center">
                <span className="material-symbols-outlined text-white text-3xl absolute animate-pulse">
                  shield
                </span>
                <div className="absolute inset-0 bg-white/10 blur-lg rounded-full"></div>
              </div>
              <span className="font-sans font-bold text-xl tracking-tight text-white">
                Vuln<span className="text-slate-400">Scanner</span>
              </span>
            </Link>
            <div className="hidden md:flex items-center space-x-4">
              <span className="text-slate-400 text-sm font-light mr-2">Already scanning?</span>
              <Link
                href="/login"
                className="text-slate-300 hover:text-white px-5 py-2 text-sm font-mono font-medium hover:bg-white/5 border border-white/10 rounded-full transition-all"
              >
                LOG_IN
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex-grow flex items-center justify-center py-20 px-4 relative z-10">
        <div className="max-w-6xl w-full mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center">
          <div className="hidden lg:flex flex-col justify-center items-start relative">
            <div className="relative w-64 h-64 mb-12 self-center lg:self-start">
              <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent rounded-full blur-3xl"></div>
              <div className="absolute inset-0 flex items-center justify-center transform hover:scale-105 transition-transform duration-700">
                <span className="material-symbols-outlined text-9xl text-white/90 drop-shadow-[0_0_35px_rgba(255,255,255,0.3)]">
                  lock_person
                </span>
              </div>
            </div>
            <h1 className="text-5xl font-bold tracking-tight text-white mb-6 leading-tight">
              Secure Your <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-300 to-gray-500">
                Digital Frontier
              </span>
            </h1>
            <p className="text-lg text-slate-400 font-light max-w-md leading-relaxed mb-8">
              Join thousands of security professionals using VulnScanner to proactively identify
              threats. Enterprise-grade protection starts with a single account.
            </p>
            <div className="flex items-center space-x-8 text-sm font-mono text-slate-500">
              <div className="flex items-center">
                <span className="material-symbols-outlined text-emerald-500 mr-2 text-lg">
                  check_circle
                </span>
                <span>SOC2 Compliant</span>
              </div>
              <div className="flex items-center">
                <span className="material-symbols-outlined text-emerald-500 mr-2 text-lg">
                  check_circle
                </span>
                <span>AES-256 Encrypted</span>
              </div>
            </div>
          </div>
          <div className="w-full max-w-md mx-auto lg:mx-0">
            <div className="glass-panel p-8 sm:p-10 rounded-[32px] border border-white/10 relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">Create Account</h2>
                <p className="text-slate-400 text-sm">
                  Start your 14-day free trial. No credit card required.
                </p>
              </div>

              <form action={handleSubmit} className="space-y-5">
                {error && (
                  <div className="bg-red-500/10 border border-red-500/50 text-red-500 text-sm p-3 rounded-lg text-center">
                    {error}
                  </div>
                )}

                <div>
                  <label
                    className="block text-xs font-mono font-medium text-slate-400 mb-1.5 ml-1 uppercase tracking-wider"
                    htmlFor="fullname"
                  >
                    Full Name
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                      <span className="material-symbols-outlined text-lg">person</span>
                    </span>
                    <input
                      className="form-input w-full rounded-xl pl-10 pr-4 py-3 text-sm focus:ring-1 focus:ring-white placeholder-slate-600 bg-white/5 border border-white/10 text-white outline-none transition-all"
                      id="fullname"
                      name="fullname"
                      placeholder="John Doe"
                      required
                      type="text"
                    />
                  </div>
                </div>
                <div>
                  <label
                    className="block text-xs font-mono font-medium text-slate-400 mb-1.5 ml-1 uppercase tracking-wider"
                    htmlFor="email"
                  >
                    Work Email
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                      <span className="material-symbols-outlined text-lg">mail</span>
                    </span>
                    <input
                      className="form-input w-full rounded-xl pl-10 pr-4 py-3 text-sm focus:ring-1 focus:ring-white placeholder-slate-600 bg-white/5 border border-white/10 text-white outline-none transition-all"
                      id="email"
                      name="email"
                      placeholder="john@company.com"
                      required
                      type="email"
                    />
                  </div>
                </div>
                <div>
                  <label
                    className="block text-xs font-mono font-medium text-slate-400 mb-1.5 ml-1 uppercase tracking-wider"
                    htmlFor="password"
                  >
                    Password
                  </label>
                  <div className="relative mb-2">
                    <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                      <span className="material-symbols-outlined text-lg">lock</span>
                    </span>
                    <input
                      className="form-input w-full rounded-xl pl-10 pr-10 py-3 text-sm focus:ring-1 focus:ring-white placeholder-slate-600 bg-white/5 border border-white/10 text-white outline-none transition-all"
                      id="password"
                      name="password"
                      placeholder="••••••••"
                      required
                      type="password"
                    />
                    <button
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-white transition-colors"
                      type="button"
                    >
                      <span className="material-symbols-outlined text-lg">visibility_off</span>
                    </button>
                  </div>
                  <div className="grid grid-cols-4 gap-1 mt-3">
                    <div className="h-1 bg-emerald-500 rounded-sm"></div>
                    <div className="h-1 bg-emerald-500/50 rounded-sm"></div>
                    <div className="h-1 bg-white/10 rounded-sm"></div>
                    <div className="h-1 bg-white/10 rounded-sm"></div>
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1 font-mono text-right">
                    Strength: Medium
                  </p>
                </div>
                <div className="flex items-start mt-2">
                  <div className="flex items-center h-5">
                    <input
                      className="w-4 h-4 rounded border-gray-600 bg-white/5 text-white focus:ring-0 focus:ring-offset-0 transition duration-150 ease-in-out cursor-pointer"
                      id="terms"
                      type="checkbox"
                    />
                  </div>
                  <div className="ml-2 text-xs text-slate-400 leading-snug">
                    <label className="cursor-pointer" htmlFor="terms">
                      I agree to the{' '}
                      <Link className="text-white hover:underline" href="#">
                        Terms of Service
                      </Link>{' '}
                      and{' '}
                      <Link className="text-white hover:underline" href="#">
                        Privacy Policy
                      </Link>
                      .
                    </label>
                  </div>
                </div>
                <button
                  className="w-full mt-6 bg-white hover:bg-gray-200 text-black font-bold py-3.5 px-8 rounded-xl shadow-glow hover:shadow-glow-hover transition-all transform hover:-translate-y-1 flex items-center justify-center group/btn disabled:opacity-50 disabled:cursor-not-allowed"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                  {!loading && (
                    <span className="material-symbols-outlined ml-2 text-lg transition-transform group-hover/btn:translate-x-1">
                      arrow_forward
                    </span>
                  )}
                </button>
              </form>
              <div className="mt-8 pt-6 border-t border-white/10 text-center">
                <p className="text-sm text-slate-400">
                  Already have an account?
                  <Link
                    className="text-white font-medium hover:text-gray-300 transition-colors inline-flex items-center ml-1 group/link"
                    href="/login"
                  >
                    Log in
                    <span className="material-symbols-outlined text-sm ml-1 opacity-0 -translate-x-2 group-hover/link:opacity-100 group-hover/link:translate-x-0 transition-all">
                      login
                    </span>
                  </Link>
                </p>
              </div>
            </div>
            <div className="mt-8 text-center lg:hidden">
              <p className="text-xs text-slate-500 font-mono">
                © 2024 VulnScanner. Secure by design.
              </p>
            </div>
          </div>
        </div>
      </div>
      <footer className="hidden lg:block absolute bottom-0 w-full py-6 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center text-xs text-slate-500 font-mono">
          <div>© 2024 VulnScanner. All rights reserved.</div>
          <div className="flex space-x-6">
            <Link className="hover:text-white transition-colors" href="#">
              Privacy
            </Link>
            <Link className="hover:text-white transition-colors" href="#">
              Terms
            </Link>
            <Link className="hover:text-white transition-colors" href="#">
              Help
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
