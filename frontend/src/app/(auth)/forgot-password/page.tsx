import Link from 'next/link';

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background-dark text-slate-200 font-sans overflow-hidden relative selection:bg-white selection:text-black">
      {/* Background Elements */}
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-stealth-gradient opacity-80"></div>
      <div className="fixed top-[-20%] left-[-10%] w-[600px] h-[600px] bg-white/5 rounded-full blur-[120px] animate-drift"></div>
      <div
        className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-gray-500/10 rounded-full blur-[120px] animate-drift"
        style={{ animationDelay: '-5s' }}
      ></div>

      <nav className="fixed w-full z-50 top-0 left-0 p-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="flex items-center cursor-pointer group">
            <div className="relative w-8 h-8 mr-3 flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-2xl absolute animate-pulse">
                shield
              </span>
              <div className="absolute inset-0 bg-white/10 blur-lg rounded-full"></div>
            </div>
            <span className="font-sans font-bold text-lg tracking-tight text-white">
              Vuln<span className="text-slate-400">Scanner</span>
            </span>
          </Link>
          <Link
            href="#"
            className="text-slate-400 hover:text-white text-sm font-mono transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-sm">help</span> Help Center
          </Link>
        </div>
      </nav>

      <main className="flex-grow flex items-center justify-center px-4 sm:px-6 relative z-10 w-full">
        <div className="w-full max-w-md">
          <div className="glass-panel p-8 sm:p-10 rounded-[24px] relative overflow-hidden bg-white/5 border border-white/10 backdrop-blur-xl shadow-glow">
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
            <div className="mb-8 text-center">
              <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-white/10 shadow-glow">
                <span className="material-symbols-outlined text-3xl text-white">lock_reset</span>
              </div>
              <h1 className="text-3xl font-bold text-white mb-3 tracking-tight">Reset Password</h1>
              <p className="text-slate-400 font-light text-sm leading-relaxed">
                Enter your email to receive a recovery link.
              </p>
            </div>
            <form className="space-y-6">
              <div>
                <label
                  className="block text-xs font-mono font-medium text-slate-300 uppercase tracking-wider mb-2 ml-1"
                  htmlFor="email"
                >
                  Email Address
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="material-symbols-outlined text-slate-500 group-focus-within:text-white transition-colors">
                      mail
                    </span>
                  </div>
                  <input
                    autoComplete="email"
                    className="form-input block w-full pl-12 pr-4 py-3.5 rounded-xl sm:text-sm bg-white/5 border border-white/10 text-white outline-none focus:bg-white/10 focus:border-white/30 transition-all placeholder-slate-500"
                    id="email"
                    name="email"
                    placeholder="name@company.com"
                    required
                    type="email"
                  />
                </div>
              </div>
              <button
                className="w-full flex justify-center items-center py-3.5 px-4 border border-transparent rounded-xl shadow-glow text-sm font-bold text-black bg-white hover:bg-gray-100 hover:shadow-glow-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-white transition-all transform hover:-translate-y-0.5"
                type="button"
              >
                Send Recovery Link
              </button>
            </form>
            <div className="mt-8 text-center">
              <Link
                className="inline-flex items-center text-sm font-medium text-slate-400 hover:text-white transition-colors group"
                href="/login"
              >
                <span className="material-symbols-outlined text-lg mr-1 transform group-hover:-translate-x-1 transition-transform">
                  chevron_left
                </span>
                Back to Login
              </Link>
            </div>
          </div>
          <div className="mt-8 flex justify-center space-x-6 text-xs font-mono text-slate-500">
            <Link className="hover:text-slate-300 transition-colors" href="#">
              PRIVACY
            </Link>
            <span className="text-slate-700">|</span>
            <Link className="hover:text-slate-300 transition-colors" href="#">
              TERMS
            </Link>
            <span className="text-slate-700">|</span>
            <Link className="hover:text-slate-300 transition-colors" href="#">
              CONTACT
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
