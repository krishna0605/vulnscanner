'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { TOTPInput } from '@/components/auth/totp-input';

type SetupStep = 'intro' | 'qr' | 'verify' | 'backup' | 'complete';

interface SetupData {
  qrCode: string;
  secret: string;
  backupCodes: string[];
}

export default function Setup2FAPage() {
  const router = useRouter();
  const [step, setStep] = useState<SetupStep>('intro');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [setupData, setSetupData] = useState<SetupData | null>(null);

  // Start setup - get QR code
  const startSetup = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/mfa/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error?.message || 'Failed to start setup');
      }

      setSetupData({
        qrCode: data.data.qrCode,
        secret: data.data.secret,
        backupCodes: [],
      });
      setStep('qr');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Verify TOTP code
  const verifyCode = useCallback(async (code: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/mfa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error?.message || 'Invalid code');
      }

      setSetupData(prev => ({
        ...prev!,
        backupCodes: data.data.backupCodes,
      }));
      setStep('backup');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Copy backup codes
  const copyBackupCodes = () => {
    if (setupData?.backupCodes) {
      navigator.clipboard.writeText(setupData.backupCodes.join('\n'));
    }
  };

  return (
    <div className="min-h-screen bg-background-dark text-slate-200 p-6">
      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/settings" 
            className="text-slate-400 hover:text-white text-sm flex items-center gap-2 mb-4"
          >
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            Back to Settings
          </Link>
          <h1 className="text-2xl font-bold text-white">Set Up Two-Factor Authentication</h1>
          <p className="text-slate-400 mt-2">
            Add an extra layer of security to your account
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-8">
          {['intro', 'qr', 'verify', 'backup'].map((s, i) => (
            <div key={s} className="flex items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                ${step === s || ['qr', 'verify', 'backup', 'complete'].indexOf(step) > i 
                  ? 'bg-white text-black' 
                  : 'bg-white/10 text-slate-500'}
              `}>
                {i + 1}
              </div>
              {i < 3 && (
                <div className={`w-12 sm:w-20 h-0.5 mx-2 ${
                  ['qr', 'verify', 'backup', 'complete'].indexOf(step) > i 
                    ? 'bg-white' 
                    : 'bg-white/10'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/50 text-red-400">
            {error}
          </div>
        )}

        {/* Step Content */}
        <div className="glass-panel rounded-[20px] p-6 sm:p-8 bg-white/5 border border-white/10">
          {/* Step 1: Introduction */}
          {step === 'intro' && (
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-white/10 flex items-center justify-center">
                <span className="material-symbols-outlined text-3xl text-white">security</span>
              </div>
              <h2 className="text-xl font-bold text-white mb-4">
                Protect Your Account with 2FA
              </h2>
              <p className="text-slate-400 mb-8">
                Two-factor authentication adds an extra layer of security by requiring a code 
                from your authenticator app in addition to your password.
              </p>
              <div className="space-y-3 text-left mb-8">
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-green-400 mt-0.5">check_circle</span>
                  <span className="text-slate-300">Works with Google Authenticator, Authy, 1Password, etc.</span>
                </div>
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-green-400 mt-0.5">check_circle</span>
                  <span className="text-slate-300">Backup codes available if you lose your device</span>
                </div>
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-green-400 mt-0.5">check_circle</span>
                  <span className="text-slate-300">Takes less than a minute to set up</span>
                </div>
              </div>
              <button
                onClick={startSetup}
                disabled={loading}
                className="w-full py-3 px-4 rounded-lg font-bold text-black bg-white hover:bg-slate-200 transition-all disabled:opacity-50"
              >
                {loading ? 'Starting...' : 'Get Started'}
              </button>
            </div>
          )}

          {/* Step 2: QR Code */}
          {step === 'qr' && setupData && (
            <div className="text-center">
              <h2 className="text-xl font-bold text-white mb-2">Scan QR Code</h2>
              <p className="text-slate-400 mb-6">
                Open your authenticator app and scan this QR code
              </p>
              
              {/* QR Code */}
              <div className="bg-white p-4 rounded-xl inline-block mb-6">
                <img 
                  src={setupData.qrCode} 
                  alt="2FA QR Code" 
                  className="w-48 h-48"
                />
              </div>

              {/* Manual Entry */}
              <details className="text-left mb-6">
                <summary className="text-slate-400 text-sm cursor-pointer hover:text-white">
                  Can&apos;t scan? Enter code manually
                </summary>
                <div className="mt-3 p-4 rounded-lg bg-white/5 border border-white/10">
                  <p className="text-xs text-slate-500 mb-2">Secret Key:</p>
                  <code className="text-white font-mono text-sm break-all">{setupData.secret}</code>
                </div>
              </details>

              <button
                onClick={() => setStep('verify')}
                className="w-full py-3 px-4 rounded-lg font-bold text-black bg-white hover:bg-slate-200 transition-all"
              >
                I&apos;ve Scanned the Code
              </button>
            </div>
          )}

          {/* Step 3: Verify */}
          {step === 'verify' && (
            <div className="text-center">
              <h2 className="text-xl font-bold text-white mb-2">Verify Setup</h2>
              <p className="text-slate-400 mb-8">
                Enter the 6-digit code from your authenticator app
              </p>
              
              <TOTPInput 
                onComplete={verifyCode}
                disabled={loading}
                error={error}
              />

              {loading && (
                <p className="mt-4 text-slate-400">Verifying...</p>
              )}
            </div>
          )}

          {/* Step 4: Backup Codes */}
          {step === 'backup' && setupData && (
            <div>
              <div className="text-center mb-6">
                <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-green-500/20 flex items-center justify-center">
                  <span className="material-symbols-outlined text-2xl text-green-400">check_circle</span>
                </div>
                <h2 className="text-xl font-bold text-white mb-2">Save Your Backup Codes</h2>
                <p className="text-slate-400">
                  Store these codes safely. You&apos;ll need them if you lose access to your authenticator.
                </p>
              </div>

              {/* Backup Codes Grid */}
              <div className="grid grid-cols-2 gap-2 mb-6 p-4 rounded-lg bg-white/5 border border-white/10">
                {setupData.backupCodes.map((code, index) => (
                  <div key={index} className="font-mono text-sm text-white text-center py-2">
                    {code}
                  </div>
                ))}
              </div>

              <div className="flex gap-3 mb-6">
                <button
                  onClick={copyBackupCodes}
                  className="flex-1 py-2 px-4 rounded-lg text-sm font-medium bg-white/10 text-white hover:bg-white/20 transition-all flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-sm">content_copy</span>
                  Copy Codes
                </button>
                <button
                  onClick={() => {
                    const blob = new Blob([setupData.backupCodes.join('\n')], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'vulnscanner-backup-codes.txt';
                    a.click();
                  }}
                  className="flex-1 py-2 px-4 rounded-lg text-sm font-medium bg-white/10 text-white hover:bg-white/20 transition-all flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-sm">download</span>
                  Download
                </button>
              </div>

              <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 mb-6">
                <p className="text-yellow-400 text-sm flex items-start gap-2">
                  <span className="material-symbols-outlined text-sm mt-0.5">warning</span>
                  Each code can only be used once. Keep them secure!
                </p>
              </div>

              <button
                onClick={() => router.push('/settings')}
                className="w-full py-3 px-4 rounded-lg font-bold text-black bg-white hover:bg-slate-200 transition-all"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
