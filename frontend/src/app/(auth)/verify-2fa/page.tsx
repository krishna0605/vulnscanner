'use client';

import { useState, useCallback, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { TOTPInput } from '@/components/auth/totp-input';

type VerifyMethod = 'totp' | 'backup' | 'email';

// Loading fallback component
function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
  );
}

// Main component wrapped in Suspense boundary
export default function Verify2FAPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Verify2FAContent />
    </Suspense>
  );
}

function Verify2FAContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const mode = searchParams.get('mode'); // 'totp', 'email', or 'email_verify'
  
  const [method, setMethod] = useState<VerifyMethod>('totp');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emailSent, setEmailSent] = useState(false);
  const [backupCode, setBackupCode] = useState('');
  const [isEmailVerifyMode, setIsEmailVerifyMode] = useState(false);

  // Initialize method based on URL mode parameter
  useEffect(() => {
    if (mode === 'email' || mode === 'email_verify') {
      setMethod('email');
      setEmailSent(true); // OTP was already sent by callback
      if (mode === 'email_verify') {
        setIsEmailVerifyMode(true);
      }
    } else if (mode === 'totp') {
      setMethod('totp');
    }
  }, [mode]);

  // Verify TOTP code
  const verifyCode = useCallback(async (code: string, type: VerifyMethod = 'totp') => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/mfa/challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, type }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error?.message || 'Invalid code');
      }

      // Verification successful - redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [router]);

  // Send email OTP
  const sendEmailOTP = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/mfa/send-email-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error?.message || 'Failed to send code');
      }

      setEmailSent(true);
      setMethod('email');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle backup code submit
  const handleBackupSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (backupCode.trim()) {
      verifyCode(backupCode.trim(), 'backup');
    }
  };

  // Get the header text based on mode
  const getHeaderText = () => {
    if (isEmailVerifyMode) {
      return {
        title: 'Verify Your Login',
        subtitle: 'Enter the verification code sent to your email',
      };
    }
    return {
      title: 'Two-Factor Authentication',
      subtitle: method === 'totp' 
        ? 'Enter the code from your authenticator app'
        : method === 'backup'
        ? 'Enter one of your backup codes'
        : 'Enter the code sent to your email',
    };
  };

  const headerText = getHeaderText();

  return (
    <div className="min-h-screen flex flex-col bg-background-dark text-slate-200 font-sans overflow-x-hidden relative">
      {/* Background Effects */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-stealth-gradient opacity-80"></div>
      <div className="fixed top-[-10%] left-[-10%] w-[800px] h-[800px] bg-white/5 rounded-full blur-[150px] animate-pulse pointer-events-none"></div>

      {/* Nav */}
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
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-grow flex items-center justify-center px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="w-full max-w-md">
          <div className="glass-panel rounded-[24px] p-8 sm:p-10 relative overflow-hidden backdrop-blur-xl border border-white/10 shadow-2xl bg-white/5">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
            
            {/* Header */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-white/5 border border-white/10 mb-4">
                <span className="material-symbols-outlined text-white">
                  {isEmailVerifyMode ? 'mail' : 'verified_user'}
                </span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">{headerText.title}</h2>
              <p className="text-slate-400 text-sm">{headerText.subtitle}</p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/50 text-red-400 text-sm text-center">
                {error}
              </div>
            )}

            {/* TOTP Input */}
            {method === 'totp' && (
              <div className="mb-8">
                <TOTPInput 
                  onComplete={(code) => verifyCode(code, 'totp')}
                  disabled={loading}
                  error={null}
                />
                {loading && (
                  <p className="mt-4 text-center text-slate-400 text-sm">Verifying...</p>
                )}
              </div>
            )}

            {/* Email OTP Input */}
            {method === 'email' && (
              <div className="mb-8">
                {emailSent && (
                  <p className="text-center text-green-400 text-sm mb-4">
                    Code sent! Check your email.
                  </p>
                )}
                <TOTPInput 
                  onComplete={(code) => verifyCode(code, 'email')}
                  disabled={loading}
                  error={null}
                />
                {loading && (
                  <p className="mt-4 text-center text-slate-400 text-sm">Verifying...</p>
                )}
                <button
                  onClick={sendEmailOTP}
                  disabled={loading}
                  className="w-full mt-4 py-2 text-sm text-slate-400 hover:text-white transition-colors"
                >
                  Didn&apos;t receive the code? Resend
                </button>
              </div>
            )}

            {/* Backup Code Input */}
            {method === 'backup' && (
              <form onSubmit={handleBackupSubmit} className="mb-8">
                <input
                  type="text"
                  value={backupCode}
                  onChange={(e) => setBackupCode(e.target.value.toUpperCase())}
                  placeholder="Enter backup code"
                  className="w-full px-4 py-3 rounded-lg text-center font-mono text-lg uppercase tracking-widest bg-white/5 border border-white/20 text-white placeholder-slate-500 focus:outline-none focus:border-white/50"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !backupCode.trim()}
                  className="w-full mt-4 py-3 px-4 rounded-lg font-bold text-black bg-white hover:bg-slate-200 transition-all disabled:opacity-50"
                >
                  {loading ? 'Verifying...' : 'Verify'}
                </button>
              </form>
            )}

            {/* Alternative Methods - Only show for TOTP users, not email_verify users */}
            {!isEmailVerifyMode && (
              <div className="border-t border-white/10 pt-6 space-y-3">
                {method !== 'totp' && (
                  <button
                    onClick={() => { setMethod('totp'); setError(null); }}
                    className="w-full py-2 text-sm text-slate-400 hover:text-white transition-colors"
                  >
                    Use authenticator app instead
                  </button>
                )}
                
                {method !== 'email' && (
                  <button
                    onClick={sendEmailOTP}
                    disabled={loading}
                    className="w-full py-2 text-sm text-slate-400 hover:text-white transition-colors flex items-center justify-center gap-2"
                  >
                    <span className="material-symbols-outlined text-sm">mail</span>
                    Email me a code instead
                  </button>
                )}
                
                {method !== 'backup' && (
                  <button
                    onClick={() => { setMethod('backup'); setError(null); }}
                    className="w-full py-2 text-sm text-slate-400 hover:text-white transition-colors flex items-center justify-center gap-2"
                  >
                    <span className="material-symbols-outlined text-sm">key</span>
                    Use a backup code
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Help Link */}
          <div className="mt-6 text-center">
            <Link 
              href="/help/2fa" 
              className="text-sm text-slate-500 hover:text-slate-300 transition-colors"
            >
              Having trouble? Get help
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
