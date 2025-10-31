export type CheckoutPlan = {
  id: string;
  name: string;
  price: number | 'custom';
  cadence?: 'mo' | 'yr';
};

export type CheckoutResponse = {
  ok: boolean;
  checkoutUrl?: string;
  error?: string;
};

export async function createCheckoutSession(plan: CheckoutPlan, csrfToken: string): Promise<CheckoutResponse> {
  // NOTE: In production, call backend API to create a Stripe Checkout Session securely.
  // This stub validates input presence and simulates latency.
  if (!plan || !plan.id || !csrfToken) {
    return { ok: false, error: 'Invalid request payload' };
  }

  // Security hint: enforce HTTPS for payment routes in production.
  const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';
  if (!isHttps) {
    // Non-blocking warning; allow in dev
    // In production you might hard-stop here.
    // return { ok: false, error: 'HTTPS required' };
  }

  await new Promise((res) => setTimeout(res, 1200));

  // Simulate a successful session creation with a placeholder URL.
  return {
    ok: true,
    checkoutUrl: 'https://checkout.stripe.com/pay/test_placeholder',
  };
}