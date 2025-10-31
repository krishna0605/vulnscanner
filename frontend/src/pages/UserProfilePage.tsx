import React from 'react';
import { Link } from 'react-router-dom';

const UserProfilePage: React.FC = () => {
  return (
    <div className="bg-[#0A0B14] text-[#E0E0E0] font-sans min-h-screen w-full">
      {/* Background */}
      <div className="absolute inset-0 -z-10 h-full w-full bg-transparent bg-[radial-gradient(#1A1A2E_1px,transparent_1px)] [background-size:32px_32px]" />
      <div className="absolute top-0 left-0 -z-10 h-1/2 w-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(0,223,252,0.18),rgba(255,255,255,0))]" />

      {/* Top navbar (reuse dashboard style) */}
      <header className="sticky top-0 z-30 w-full border-b border-[#2E2E3F]/50 bg-[#0A0B14]/80 px-4 py-3 backdrop-blur-sm sm:px-6 lg:px-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/dashboard" className="flex items-center gap-3 cursor-pointer">
              <div
                className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9"
                style={{
                  backgroundImage:
                    'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAoGb6izEyw_X-IY8P4G1a15e7o30ltLXJVnqKuWW_bw3qlnzlNNTYrEnkZXhnNLOZHJAuVURDsIy0yKJ7KWbV5ulHg8NFsUL2QIoXSgs3tLTs46S3zXpP3WpI1co60H8nXr7VC9fJbj0cdMT5dL9n4F2bRQo20AdUqCu9h7m8G7YlLEnUZVXjv39K5ticnvVqwC6wCVyIQxyYAJcZ9UhO93dRoTmg_8WKC7IOoAhK-PraBlN-2I9Qr5IK5rlI__qB-QTLv_Fmr4eNx")',
                }}
              />
              <div className="flex flex-col">
                <h1 className="text-[#E0E0E0] text-base font-bold leading-normal">VulnScanner</h1>
              </div>
            </Link>
            <nav className="hidden md:flex items-center gap-4">
              <Link to="/dashboard" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all"><span className="material-symbols-outlined text-base">dashboard</span>Dashboard</Link>
              <button type="button" aria-disabled="true" title="Coming soon" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all cursor-not-allowed"><span className="material-symbols-outlined text-base">radar</span>Scans</button>
              <button type="button" aria-disabled="true" title="Coming soon" className="nav-link relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-[#888888] transition-all cursor-not-allowed"><span className="material-symbols-outlined text-base">folder</span>Projects</button>
              <Link to="/profile" className="nav-link active relative flex items-center gap-2 px-2 py-2 text-sm font-medium leading-normal text-white transition-all"><span className="material-symbols-outlined text-base">settings</span>Settings</Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <button className="relative flex cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 w-10 bg-[#131523]/80 text-[#E0E0E0] hover:text-[#00DFFC] transition-colors">
              <span className="material-symbols-outlined">notifications</span>
              <div className="absolute top-1.5 right-1.5 size-2.5 rounded-full bg-[#FF4C4C] border-2 border-[#131523]" />
            </button>
            <div
              className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10"
              style={{
                backgroundImage:
                  'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAHfrmUAygQFu0IYf15YygLz1M-mFmnyP5WykkDqeELmtLtxAVBzAMQk43miTHIotrguAKBeiuU4KX8U1ZKG_dFjMejJ84ikM_rq7yR8Ss4nR1lfPj0KnhtHH_5HWGg6nJgs74Bg_s8SDjLD_wMh6FFMEJQlmTrQos_Fm-62FS_Cd6g-tNcGAvltwt5yInrDMY4kB7Q3nM3IzFRJGkeWvV3zitN6Ol7FFIH2XhLSYnShvhhqEy5uipUYVMH_tnOrUup9UA6X6Mwgtez")',
              }}
            />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex flex-1 justify-center py-10 px-4 sm:px-6 lg:px-10">
        <div className="flex flex-col w-full max-w-4xl gap-8">
          <div>
            <h1 className="text-white text-4xl font-black leading-tight tracking-[-0.033em]">Profile & Settings</h1>
          </div>

          {/* Account Information */}
          <section className="flex flex-col gap-6 rounded-xl border border-[#2E2E3F]/60 bg-[#131523]/80 p-6 backdrop-blur-sm">
            <div className="flex items-center gap-6">
              <div className="relative">
                <div
                  className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-20"
                  style={{
                    backgroundImage:
                      'url("https://lh3.googleusercontent.com/aida-public/AB6AXuD1uVDcZeylK1xUbVAeGGJzVoIH8-5OUi5Pvx2oxzxmeam_zZWmcj7zE5kp5nYb6trhFCYsAhpic8yILSiYeq8M8iIY54LbNGqPFDe6DKWy05uCGVJXIAzDfRVkGXFba0xM6zSB5gT_e_U7xNRsFfnBzCMMqgNdPKTM3IJhPmiXM62LXYUP6XpwlD2Odr-rxbmdWPt8ZMnzNlZGspikGuaN6HgKSJbEOqaa5235QitxfUIoq5-ds8ppP_H0lpBaOCoGAHMXsbAa5HhS")',
                  }}
                />
                <button className="absolute bottom-0 right-0 flex items-center justify-center size-7 rounded-full bg-[#00DFFC] text-[#0A0B14] hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-base">edit</span>
                </button>
              </div>
              <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">Account Information</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <label className="flex flex-col w-full">
                <p className="text-[#888888] text-sm font-medium leading-normal pb-2">Full Name</p>
                <div className="rounded-lg border border-[#2E2E3F] bg-[#0A0B14] transition-all glow-on-focus">
                  <input className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#E0E0E0] focus:outline-0 focus:ring-0 border-none bg-transparent h-12 placeholder:text-[#888888] px-4 text-base" defaultValue="Alex Volkov" />
                </div>
              </label>
              <label className="flex flex-col w-full">
                <p className="text-[#888888] text-sm font-medium leading-normal pb-2">Email Address</p>
                <div className="rounded-lg border border-[#2E2E3F] bg-[#0A0B14]">
                  <input className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#888888] focus:outline-0 focus:ring-0 border-none bg-transparent h-12 px-4 text-base" readOnly defaultValue="alex.v@securenet.io" />
                </div>
              </label>
            </div>
            <div className="flex justify-end">
              <button className="flex items-center justify-center rounded-lg h-10 bg-[#00DFFC] text-[#0A0B14] gap-2 text-sm font-bold leading-normal px-5 transition-all btn-glow-on-hover hover:bg-opacity-90">Save Changes</button>
            </div>
          </section>

          {/* Preferences */}
          <section className="flex flex-col gap-6 rounded-xl border border-[#2E2E3F]/60 bg-[#131523]/80 p-6 backdrop-blur-sm">
            <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">Preferences</h2>
            <div className="flex flex-col gap-4">
              {/* Dark Theme */}
              <div className="flex justify-between items-center p-3 rounded-lg hover:bg-[#0A0B14]/50">
                <div>
                  <p className="text-[#E0E0E0] font-medium">Dark Theme</p>
                  <p className="text-[#888888] text-sm">Embrace the darkness for a focused experience.</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input defaultChecked className="sr-only peer" type="checkbox" />
                  <div className="w-11 h-6 bg-[#2E2E3F] rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#00DFFC]"></div>
                </label>
              </div>
              {/* Email on Scan Completion */}
              <div className="flex justify-between items-center p-3 rounded-lg hover:bg-[#0A0B14]/50">
                <div>
                  <p className="text-[#E0E0E0] font-medium">Email on Scan Completion</p>
                  <p className="text-[#888888] text-sm">Get notified when your security scans are complete.</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input defaultChecked className="sr-only peer" type="checkbox" />
                  <div className="w-11 h-6 bg-[#2E2E3F] rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#00DFFC]"></div>
                </label>
              </div>
              {/* In-App Alerts */}
              <div className="flex justify-between items-center p-3 rounded-lg hover:bg-[#0A0B14]/50">
                <div>
                  <p className="text-[#E0E0E0] font-medium">In-App Alerts</p>
                  <p className="text-[#888888] text-sm">Receive real-time notifications within the app.</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input className="sr-only peer" type="checkbox" />
                  <div className="w-11 h-6 bg-[#2E2E3F] rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#00DFFC]"></div>
                </label>
              </div>
            </div>
            <div className="flex justify-end mt-2">
              <button className="flex items-center justify-center rounded-lg h-10 bg-[#00DFFC] text-[#0A0B14] gap-2 text-sm font-bold leading-normal px-5 transition-all btn-glow-on-hover hover:bg-opacity-90">Save Changes</button>
            </div>
          </section>

          {/* API Management */}
          <section className="flex flex-col gap-6 rounded-xl border border-[#2E2E3F]/60 bg-[#131523]/80 p-6 backdrop-blur-sm">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">API Management</h2>
                <p className="text-[#888888] text-sm mt-1">Manage your API keys for programmatic access.</p>
              </div>
              <button className="flex items-center justify-center rounded-lg h-10 bg-[#00DFFC]/20 text-[#00DFFC] border border-[#00DFFC]/50 gap-2 text-sm font-bold leading-normal px-4 transition-all hover:bg-[#00DFFC]/30 glow-on-hover">
                <span className="material-symbols-outlined text-lg">add</span>
                Generate New Key
              </button>
            </div>
            <div className="flex flex-col gap-3">
              <div className="flex justify-between items-center p-3 rounded-lg bg-[#0A0B14]">
                <div className="flex items-center gap-4">
                  <span className="material-symbols-outlined text-[#00DFFC]">key</span>
                  <p className="font-mono text-sm text-[#E0E0E0]">prod_key_•••••••••••••••••••••••••a4f2</p>
                </div>
                <div className="flex items-center gap-2">
                  <button className="flex items-center justify-center rounded-md h-8 w-8 text-[#888888] hover:text-white hover:bg-[#2E2E3F] transition-colors">
                    <span className="material-symbols-outlined text-xl">content_copy</span>
                  </button>
                  <button className="flex items-center justify-center rounded-md h-8 w-8 text-[#FF4C4C]/70 hover:text-[#FF4C4C] hover:bg-[#FF4C4C]/10 transition-colors">
                    <span className="material-symbols-outlined text-xl">delete</span>
                  </button>
                </div>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-[#0A0B14]">
                <div className="flex items-center gap-4">
                  <span className="material-symbols-outlined text-[#00DFFC]">key</span>
                  <p className="font-mono text-sm text-[#E0E0E0]">dev_key_••••••••••••••••••••••••••b1c8</p>
                </div>
                <div className="flex items-center gap-2">
                  <button className="flex items-center justify-center rounded-md h-8 w-8 text-[#888888] hover:text-white hover:bg-[#2E2E3F] transition-colors">
                    <span className="material-symbols-outlined text-xl">content_copy</span>
                  </button>
                  <button className="flex items-center justify-center rounded-md h-8 w-8 text-[#FF4C4C]/70 hover:text-[#FF4C4C] hover:bg-[#FF4C4C]/10 transition-colors">
                    <span className="material-symbols-outlined text-xl">delete</span>
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Security */}
          <section className="flex flex-col gap-6 rounded-xl border border-[#2E2E3F]/60 bg-[#131523]/80 p-6 backdrop-blur-sm">
            <h2 className="text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">Security</h2>
            <div className="flex flex-col gap-4">
              <div className="flex justify-between items-center p-3 rounded-lg hover:bg-[#0A0B14]/50">
                <div>
                  <p className="text-[#E0E0E0] font-medium">Change Password</p>
                  <p className="text-[#888888] text-sm">Last changed 3 months ago.</p>
                </div>
                <button className="flex items-center justify-center rounded-lg h-10 bg-[#0A0B14] border border-[#2E2E3F] text-[#E0E0E0] gap-2 text-sm font-bold leading-normal px-4 transition-colors hover:border-[#888888]">Change Password</button>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg hover:bg-[#0A0B14]/50">
                <div>
                  <p className="text-[#E0E0E0] font-medium">Two-Factor Authentication (2FA)</p>
                  <p className="text-[#888888] text-sm">Add an extra layer of security to your account.</p>
                </div>
                <button className="flex items-center justify-center rounded-lg h-10 bg-[#00C853]/10 border border-[#00C853]/30 text-[#00C853] gap-2 text-sm font-bold leading-normal px-4 transition-colors hover:bg-[#00C853]/20">
                  <span className="material-symbols-outlined text-lg">verified_user</span>
                  Enable 2FA
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default UserProfilePage;