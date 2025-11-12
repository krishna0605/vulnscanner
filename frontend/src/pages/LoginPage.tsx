import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { loginStart, loginSuccess, loginFailure } from '../store/slices/authSlice.ts';
import { RootState } from '../store';
import { useAuth } from '../contexts/AuthContext.tsx';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const redirect = params.get('redirect') || '/dashboard';
  const pendingPurchase = typeof window !== 'undefined' ? sessionStorage.getItem('pendingPurchase') : null;
  const { loading, error } = useSelector((state: RootState) => state.auth);
  
  // Local backend auth via AuthContext
  const { signIn, loading: authLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      dispatch(loginFailure('Please enter both email and password'));
      return;
    }
    
    // Don't clear credentials during authentication
    dispatch(loginStart());
    setSuccessMessage('');
    
    try {
      const { user, error } = await signIn(email, password);
      if (error) {
        throw new Error(error?.message || 'Invalid credentials');
      }
      dispatch(loginSuccess({ email: user?.email || email }));
      setSuccessMessage('Login successful! Redirecting to dashboard...');
      setTimeout(() => {
        setEmail('');
        setPassword('');
        navigate(redirect, { replace: true });
      }, 1500);
    } catch (apiErr: any) {
      dispatch(loginFailure(apiErr?.message || 'Login failed'));
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center p-4 overflow-hidden bg-background-dark font-sans text-text-light">
      {/* Background elements */}
      <div className="absolute inset-0 z-0 bg-animated-subtle animate-subtle-pan"></div>
      <div className="absolute inset-0 z-0 bg-aurora-subtle"></div>
      
      {/* Login card */}
      <div className="relative z-10 w-full max-w-sm rounded-lg border border-border-dark bg-surface-dark p-8 shadow-2xl shadow-black/50 backdrop-blur-sm">
        {/* Logo and header */}
        <div className="flex flex-col items-center gap-2 mb-8">
          <div className="flex items-center justify-center h-14 w-14 rounded-full border border-primary-faint bg-primary/10 text-primary shadow-glow">
            <span className="material-symbols-outlined text-3xl" style={{ fontVariationSettings: "'wght' 300" }}>security</span>
          </div>
          <h1 className="text-white text-2xl font-medium tracking-wide">Scanner Access</h1>
          <p className="text-text-dark text-sm font-light">Please sign in to continue</p>
        </div>
        
        {/* Purchase notice */}
        {pendingPurchase && (
          <div className="mb-4 rounded-md border border-[#0ea5e9]/30 bg-[#0ea5e9]/10 p-3 text-[#0ea5e9] text-sm">
            Sign in required to continue your purchase. You’ll return to checkout after login.
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          {/* Email field */}
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
          
          {/* Password field */}
          <div>
            <div className="input-glow-wrapper relative flex items-center rounded-md border border-border-dark bg-[#030712] transition-all duration-300">
              <span className="material-symbols-outlined text-text-dark absolute left-3 transition-colors duration-300">lock</span>
              <input 
                className="form-input w-full appearance-none bg-transparent h-11 pl-10 pr-10 text-text-light placeholder:text-text-dark focus:outline-none focus:ring-0 text-base font-normal" 
                id="password" 
                placeholder="Password" 
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button 
                type="button"
                aria-label="Toggle password visibility" 
                className="text-text-dark absolute right-3 hover:text-white transition-colors"
                onClick={togglePasswordVisibility}
              >
                <span className="material-symbols-outlined text-xl">
                  {showPassword ? "visibility" : "visibility_off"}
                </span>
              </button>
            </div>
          </div>
          
          {/* Remember me and forgot password */}
          <div className="flex flex-row items-center justify-between">
            <label className="flex items-center gap-x-2.5 cursor-pointer group">
              <div className="relative">
                <input 
                  className="peer sr-only" 
                  type="checkbox"
                  checked={rememberMe}
                  onChange={() => setRememberMe(!rememberMe)}
                />
                <div className="relative w-9 h-5 bg-[#030712] border border-border-dark rounded-full peer peer-checked:bg-primary/20 peer-checked:border-primary-faint transition-all duration-300"></div>
                <div className={`absolute left-1 top-1 h-3 w-3 rounded-full ${rememberMe ? 'bg-primary translate-x-4 shadow-[0_0_8px_var(--color-primary)]' : 'bg-text-dark'} transition-all duration-300`}></div>
              </div>
              <p className="text-text-light text-sm font-normal select-none">Remember me</p>
            </label>
            <Link to="/forgot-password" className="text-sm font-medium text-text-dark link-subtle">Forgot Password?</Link>
          </div>
          
          {/* Login button */}
          <div className="pt-2">
            <button 
              type="submit"
              disabled={loading || authLoading}
              className="btn-trail relative flex w-full cursor-pointer items-center justify-center overflow-hidden rounded-md h-11 px-5 text-base font-medium tracking-wide text-white bg-primary/20 border border-primary-faint hover:bg-primary/30 transition-colors duration-300"
            >
              {(loading || authLoading) ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                <span>Login</span>
              )}
            </button>
          </div>
          
          {/* Success message */}
          {successMessage && (
            <div className="text-green-500 text-sm text-center mt-2 flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {successMessage}
            </div>
          )}

          {/* Error message */}
          {error && !successMessage && (
            <div className="text-red-500 text-sm text-center mt-2">
              {error}
            </div>
          )}
          
          {/* Register link */}
          <div className="text-center pt-4">
            <p className="text-sm text-text-dark">
              Don't have an account?
              <Link to="/register" className="font-medium text-primary link-subtle ml-1">Register</Link>
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

export default LoginPage;