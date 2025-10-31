import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
// Call backend to create a checkout session
const createCheckoutSession = async (
  plan: { id: string; name: string; price: number | 'custom'; cadence?: 'mo' | 'yr' },
  csrfToken: string
) => {
  if (!plan || !plan.id || !csrfToken) {
    return { ok: false, error: 'Invalid request payload' } as { ok: boolean; checkoutUrl?: string; error?: string };
  }
  const API_BASE_URL = (process.env as any)?.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
  try {
    const res = await fetch(`${API_BASE_URL}/api/payments/checkout?plan_id=${encodeURIComponent(plan.id)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-csrf-token': csrfToken,
      },
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      return { ok: false, error: data?.detail || 'Failed to create checkout session' };
    }
    const data = await res.json();
    return { ok: true, checkoutUrl: data?.checkout_url };
  } catch (e: any) {
    return { ok: false, error: e?.message || 'Network error' };
  }
};

type Plan = {
  id: string;
  name: string;
  price: number | 'custom';
  cadence?: 'mo' | 'yr';
};

const getPendingPurchase = (): Plan | null => {
  try {
    const raw = sessionStorage.getItem('pendingPurchase');
    return raw ? JSON.parse(raw) as Plan : null;
  } catch {
    return null;
  }
};

const clearPendingPurchase = () => {
  try {
    sessionStorage.removeItem('pendingPurchase');
  } catch {}
};

const ensureCsrfToken = (): string => {
  let token = sessionStorage.getItem('csrfToken');
  if (!token) {
    token = Math.random().toString(36).slice(2) + Date.now().toString(36);
    sessionStorage.setItem('csrfToken', token);
  }
  return token;
};

const StripeCheckoutPage: React.FC = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState<string>('');

  const plan = useMemo(() => getPendingPurchase(), []);
  const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';

  useEffect(() => {
    // If no plan is available, guide user back to pricing
    if (!plan) {
      setMessage('No active purchase found. Please choose a plan.');
    }
  }, [plan]);

  const beginCheckout = async () => {
    if (!plan) {
      setMessage('No plan selected.');
      return;
    }
    setStatus('loading');
    setMessage('Initializing secure payment session...');

    try {
      const csrfToken = ensureCsrfToken();
      const res = await createCheckoutSession(plan, csrfToken);
      if (!res.ok) {
        throw new Error(res.error || 'Failed to create session');
      }
      setStatus('success');
      setMessage('Payment session initialized. Redirecting to Stripe...');
      clearPendingPurchase();
      // In real integration, use: window.location.href = res.checkoutUrl!
    } catch (err) {
      setStatus('error');
      setMessage('Failed to initialize payment. Please try again.');
    }
  };

  const cancelAndReturn = () => {
    clearPendingPurchase();
    navigate('/pricing');
  };

  return (
    <div className="min-h-screen relative overflow-x-hidden bg-[#0B0D12] text-[#e2e8f0]">
      <div className="animated-bg" />
      <div className="bg-animated-subtle absolute inset-0" />
      <header className="flex items-center justify-between px-6 py-4 mx-auto max-w-5xl">
        <h2 className="text-[#F0F0F0] text-xl font-bold tracking-[-0.015em]">Secure Checkout</h2>
        <button onClick={() => navigate('/pricing')} className="link-subtle text-[#C8C8D6]">Back to Pricing</button>
      </header>

      <main className="px-6 py-8 mx-auto max-w-5xl">
        {!isHttps && (
          <div className="mb-4 rounded-md border border-yellow-500/30 bg-yellow-600/10 p-3 text-yellow-300 text-sm">
            You are on an insecure origin (HTTP). Stripe requires HTTPS in production.
          </div>
        )}

        <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
          {plan ? (
            <div>
              <h3 className="text-lg font-semibold text-[#F0F0F0]">Plan Summary</h3>
              <p className="mt-1 text-[#A0A0B0]">{plan.name} {plan.price !== 'custom' ? `$${plan.price}/${plan.cadence ?? 'mo'}` : 'Custom pricing'}</p>

              <div className="mt-6 flex items-center gap-4">
                <button
                  onClick={beginCheckout}
                  disabled={status === 'loading'}
                  className="btn-trail cursor-pointer flex items-center justify-center rounded-md h-11 px-5 text-base font-medium text-white bg-primary/20 border border-primary-faint hover:bg-primary/30 disabled:opacity-60"
                >
                  {status === 'loading' ? 'Starting...' : 'Proceed to Secure Checkout'}
                </button>

                <button onClick={cancelAndReturn} className="flex items-center justify-center rounded-md h-11 px-5 text-base font-medium text-[#0ea5e9] bg-transparent border border-primary-faint/40 hover:bg-primary/10">
                  Cancel
                </button>
              </div>

              {message && (
                <p className="mt-4 text-sm text-[#C8C8D6]">{message}</p>
              )}

              {status === 'success' && (
                <div className="mt-4 rounded-md border border-green-500/30 bg-green-600/10 p-3 text-green-300 text-sm">
                  Payment session created. In production, you would be redirected to Stripe.
                </div>
              )}
              {status === 'error' && (
                <div className="mt-4 rounded-md border border-red-500/30 bg-red-600/10 p-3 text-red-300 text-sm">
                  Something went wrong. Please retry or contact support.
                </div>
              )}
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-semibold text-[#F0F0F0]">No Active Purchase</h3>
              <p className="mt-2 text-sm text-[#C8C8D6]">Choose a plan first. We’ll bring you back here after login if needed.</p>
              <button onClick={() => navigate('/pricing')} className="mt-4 btn-trail cursor-pointer flex items-center justify-center rounded-md h-11 px-5 text-base font-medium text-white bg-primary/20 border border-primary-faint hover:bg-primary/30">Go to Pricing</button>
            </div>
          )}
        </div>

        <div className="mt-8 text-xs text-[#8C8CA0]">
          By proceeding, you agree to our Terms and confirm you’re on a secure network.
        </div>
      </main>
    </div>
  );
};

export default StripeCheckoutPage;