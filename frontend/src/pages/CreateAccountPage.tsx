import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.tsx';

const CreateAccountPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [organization, setOrganization] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();
  
  // Local backend auth via AuthContext
  const { signUp } = useAuth();
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    if (!email || !password) {
      setError('Please enter email and password');
      return;
    }
    
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }
    
    setLoading(true);
    
    try {
      const { user, error } = await signUp(email, password, fullName || undefined);
      if (error) {
        throw new Error(error?.message || 'Registration failed');
      }
      setSuccess('Account created! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (apiErr: any) {
      setError(apiErr?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center p-4 overflow-hidden bg-background-dark font-sans text-text-light">
      {/* Background elements */}
      <div className="absolute inset-0 z-0 bg-animated-subtle"></div>
      <div className="absolute inset-0 z-0 bg-aurora-subtle"></div>

      {/* Register card */}
      <div className="relative z-10 w-full max-w-sm rounded-lg border border-border-dark bg-surface-dark p-8 shadow-2xl shadow-black/50 backdrop-blur-sm">
        {/* Logo and header */}
        <div className="flex flex-col items-center gap-2 mb-8">
          <div className="flex items-center justify-center h-14 w-14 rounded-full border border-primary-faint bg-primary/10 text-primary shadow-glow">
            <span className="material-symbols-outlined text-3xl" style={{ fontVariationSettings: "'wght' 300" }}>person_add</span>
          </div>
          <h1 className="text-white text-2xl font-medium tracking-wide">Create Account</h1>
          <p className="text-text-dark text-sm font-light">Join to start scanning</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {/* Full name */}
          <div>
            <div className="input-glow-wrapper relative flex items-center rounded-md border border-border-dark bg-[#030712] transition-all duration-300">
              <span className="material-symbols-outlined text-text-dark absolute left-3 transition-colors duration-300">person</span>
              <input
                className="form-input w-full appearance-none bg-transparent h-11 pl-10 pr-4 text-text-light placeholder:text-text-dark focus:outline-none focus:ring-0 text-base font-normal"
                id="fullname"
                placeholder="Full Name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          </div>

          {/* Organization */}
          <div>
            <div className="input-glow-wrapper relative flex items-center rounded-md border border-border-dark bg-[#030712] transition-all duration-300">
              <span className="material-symbols-outlined text-text-dark absolute left-3 transition-colors duration-300">corporate_fare</span>
              <input
                className="form-input w-full appearance-none bg-transparent h-11 pl-10 pr-4 text-text-light placeholder:text-text-dark focus:outline-none focus:ring-0 text-base font-normal"
                id="organization"
                placeholder="Organization"
                type="text"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
              />
            </div>
          </div>

          {/* Email */}
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

          {/* Password */}
          <div>
            <div className="input-glow-wrapper relative flex items-center rounded-md border border-border-dark bg-[#030712] transition-all duration-300">
              <span className="material-symbols-outlined text-text-dark absolute left-3 transition-colors duration-300">lock</span>
              <input
                className="form-input w-full appearance-none bg-transparent h-11 pl-10 pr-10 text-text-light placeholder:text-text-dark focus:outline-none focus:ring-0 text-base font-normal"
                id="password"
                placeholder="Password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                aria-label="Toggle password visibility"
                className="text-text-dark absolute right-3 hover:text-white transition-colors"
                onClick={() => setShowPassword(!showPassword)}
              >
                <span className="material-symbols-outlined text-xl">
                  {showPassword ? 'visibility' : 'visibility_off'}
                </span>
              </button>
            </div>
          </div>

          {/* Submit */}
          <div className="pt-2">
            <button disabled={loading} className="btn-trail relative flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-md h-11 px-5 text-base font-medium tracking-wide text-white bg-primary/20 border border-primary-faint hover:bg-primary/30 transition-colors duration-300 disabled:opacity-50">
              <span>{loading ? 'Registering...' : 'Register'}</span>
            </button>
          </div>

          {/* Status messages */}
          {error && (
            <div className="mt-2 text-sm text-red-400" role="alert">{error}</div>
          )}
          {success && (
            <div className="mt-2 text-sm text-green-400" role="status">{success}</div>
          )}

          {/* Sign in link */}
          <div className="text-center pt-4">
            <p className="text-sm text-text-dark">
              Already have an account?
              <Link to="/login" className="font-medium text-primary link-subtle ml-1">Sign In</Link>
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

export default CreateAccountPage;