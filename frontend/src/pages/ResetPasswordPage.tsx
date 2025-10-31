import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const ResetPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email) {
      setError('Please enter your email');
      return;
    }
    setLoading(true);
    try {
      const API_BASE_URL = (process.env as any)?.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${API_BASE_URL}/api/auth/forgot-password?email=${encodeURIComponent(email)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.detail || 'Request failed');
      }
      setSent(true);
    } catch (err: any) {
      setError(err?.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center p-4 overflow-hidden bg-background-dark font-sans text-text-light">
      {/* Background elements */}
      <div className="absolute inset-0 z-0 bg-animated-subtle"></div>
      <div className="absolute inset-0 z-0 bg-aurora-subtle"></div>

      {/* Card */}
      <div className="relative z-10 w-full max-w-sm rounded-lg border border-border-dark bg-surface-dark p-8 shadow-2xl shadow-black/50 backdrop-blur-sm">
        <div className="flex flex-col items-center gap-2 mb-8">
          <div className="flex items-center justify-center h-14 w-14 rounded-full border border-primary-faint bg-primary/10 text-primary shadow-glow">
            <span className="material-symbols-outlined text-3xl" style={{ fontVariationSettings: "'wght' 300" }}>lock_reset</span>
          </div>
          <h1 className="text-white text-2xl font-medium tracking-wide">Reset Password</h1>
          <p className="text-text-dark text-sm font-light text-center">Enter your email to receive a password reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div>
            <div className="input-glow-wrapper relative flex items-center rounded-md border border-border-dark bg-[#030712] transition-all duration-300">
              <span className="material-symbols-outlined text-text-dark absolute left-3 transition-colors duration-300">mail</span>
              <input
                className="form-input w-full appearance-none bg-transparent h-11 pl-10 pr-4 text-text-light placeholder:text-text-dark focus:outline-none focus:ring-0 text-base font-normal"
                id="email"
                placeholder="email@example.com"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="pt-2">
            <button type="submit" disabled={loading} className="btn-trail relative flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-md h-11 px-5 text-base font-medium tracking-wide text-white bg-primary/20 border border-primary-faint hover:bg-primary/30 transition-colors duration-300 disabled:opacity-50">
              <span>{sent ? 'Link Sent' : loading ? 'Sending...' : 'Send Reset Link'}</span>
            </button>
            {error && (
              <div className="mt-2 text-sm text-red-400" role="alert">{error}</div>
            )}
          </div>

          <div className="text-center pt-2">
            <p className="text-sm text-text-dark">
              Remembered your password?
              <Link to="/login" className="font-medium text-primary link-subtle ml-1">Back to Login</Link>
            </p>
          </div>
        </form>
      </div>

      {/* Footer */}
      <div className="absolute bottom-4 text-center w-full px-4">
        <p className="text-xs text-text-dark/50">© 2024 SecureScan Dynamics. All rights reserved.</p>
      </div>
    </div>
  );
};

export default ResetPasswordPage;