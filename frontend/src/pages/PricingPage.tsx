import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

const PricingPage: React.FC = () => {
  const navigate = useNavigate();
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  const startPurchase = (plan: { id: string; name: string; price: number | 'custom'; cadence?: 'mo' | 'yr' }) => {
    // Save selected plan so we can recover after login
    try {
      sessionStorage.setItem('pendingPurchase', JSON.stringify(plan));
    } catch {}

    if (!isAuthenticated) {
      // Redirect unauthenticated users to login, then back to checkout
      navigate(`/login?redirect=${encodeURIComponent('/checkout')}`);
      return;
    }
    navigate('/checkout');
  };

  return (
    <div className="min-h-screen relative overflow-x-hidden bg-[#0B0D12] text-[#e2e8f0]">
      {/* Subtle animated background */}
      <div className="animated-bg" />
      <div className="bg-animated-subtle absolute inset-0" />

      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 mx-auto max-w-7xl">
        <div className="flex items-center gap-3 text-[#F0F0F0]">
          <div className="text-[#0ea5e9]">
            <svg className="h-8 w-8" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path fill="currentColor" fillRule="evenodd" d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z" />
            </svg>
          </div>
          <h2 className="text-[#F0F0F0] text-xl font-bold tracking-[-0.015em]">VulnScanner</h2>
        </div>
        <nav className="hidden md:flex items-center gap-6 text-sm ml-6">
          <Link to="/" className="link-subtle text-[#C8C8D6]">Home</Link>
          <a href="#plans" className="link-subtle text-[#C8C8D6]">Plans</a>
          <a href="#faq" className="link-subtle text-[#C8C8D6]">FAQ</a>
          <Link to="/login" className="link-subtle text-[#C8C8D6]">Login</Link>
        </nav>
        <div className="flex gap-3 ml-6 md:ml-8">
          <Link to="/register" className="btn-trail cursor-pointer flex items-center justify-center rounded-lg h-10 px-5 bg-[#0ea5e9] text-[#0B0D12] text-sm font-bold glow-on-hover">Sign Up</Link>
        </div>
      </header>

      {/* Pricing */}
      <main className="px-6 py-12 mx-auto max-w-7xl grid-overlay">
        <section id="plans" className="text-center mb-12">
          <h1 className="text-3xl font-bold text-[#F0F0F0] tracking-tight">Pricing Options</h1>
          <p className="text-[#A0A0B0] text-sm sm:text-base mt-2">Choose the plan that fits your team.</p>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Starter */}
          <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm h-full min-h-[320px] flex flex-col">
            <h3 className="text-xl font-semibold text-[#F0F0F0]">Starter</h3>
            <p className="mt-1 text-[#A0A0B0]">Best for solo developers</p>
            <div className="mt-4 flex items-end gap-1">
              <span className="text-3xl font-bold text-[#F0F0F0]">$19</span>
              <span className="text-[#8C8CA0]">/mo</span>
            </div>
            <ul className="mt-4 space-y-2 text-sm text-[#C8C8D6]">
              <li>Single project</li>
              <li>5 scans/month</li>
              <li>Basic reports</li>
            </ul>
            <button
              onClick={() => startPurchase({ id: 'starter', name: 'Starter', price: 19, cadence: 'mo' })}
              className="btn-trail cursor-pointer mt-auto flex w-full h-11 items-center justify-center rounded-md px-5 text-base font-medium text-white text-center bg-primary/20 border border-primary-faint hover:bg-primary/30"
            >
              Choose Starter
            </button>
          </div>

          {/* Pro */}
          <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm h-full min-h-[320px] flex flex-col">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-semibold text-[#F0F0F0]">Pro</h3>
              <span className="rounded-full px-2.5 py-0.5 text-xs bg-[#0ea5e9]/15 text-[#0ea5e9]">Popular</span>
            </div>
            <p className="mt-1 text-[#A0A0B0]">Teams shipping weekly</p>
            <div className="mt-4 flex items-end gap-1">
              <span className="text-3xl font-bold text-[#F0F0F0]">$99</span>
              <span className="text-[#8C8CA0]">/mo</span>
            </div>
            <ul className="mt-4 space-y-2 text-sm text-[#C8C8D6]">
              <li>Unlimited projects</li>
              <li>Priority scans</li>
              <li>Advanced analytics</li>
            </ul>
            <button
              onClick={() => startPurchase({ id: 'pro', name: 'Pro', price: 99, cadence: 'mo' })}
              className="btn-trail cursor-pointer mt-auto flex w-full h-11 items-center justify-center rounded-md px-5 text-base font-medium text-white text-center bg-primary/20 border border-primary-faint hover:bg-primary/30"
            >
              Choose Pro
            </button>
          </div>

          {/* Enterprise */}
          <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm h-full min-h-[320px] flex flex-col">
            <h3 className="text-xl font-semibold text-[#F0F0F0]">Enterprise</h3>
            <p className="mt-1 text-[#A0A0B0]">Compliance-driven orgs</p>
            <div className="mt-4 flex items-end gap-1">
              <span className="text-3xl font-bold text-[#F0F0F0]">Custom</span>
            </div>
            <ul className="mt-4 space-y-2 text-sm text-[#C8C8D6]">
              <li>SOC2, ISO27001 support</li>
              <li>Guided remediation</li>
              <li>Dedicated support</li>
            </ul>
            <Link to="/login" className="btn-trail cursor-pointer mt-auto flex w-full h-11 items-center justify-center rounded-md px-5 text-base font-medium text-white text-center bg-primary/20 border border-primary-faint hover:bg-primary/30">Contact Sales</Link>
          </div>
        </div>

        {/* FAQ placeholder */}
        <section id="faq" className="mt-16">
          <h2 className="text-[#F0F0F0] text-2xl font-bold">Frequently Asked Questions</h2>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-[#C8C8D6]">
            <div>
              <h3 className="text-[#F0F0F0] font-semibold">Can I change plans later?</h3>
              <p className="mt-2">Yes, you can switch plans anytime from your account settings.</p>
            </div>
            <div>
              <h3 className="text-[#F0F0F0] font-semibold">Do you offer trials?</h3>
              <p className="mt-2">We offer a 14-day trial on Pro. No credit card required.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default PricingPage;