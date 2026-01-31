'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
// Using simpler icons for the top nav or keeping it text-based for a cleaner look
import { Bell, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';

const navItems = [
  { title: 'Dashboard', href: '/dashboard' },
  { title: 'Projects', href: '/projects' },
  { title: 'Scans', href: '/scans' },
  { title: 'Reports', href: '/reports' },
  { title: 'Settings', href: '/settings' },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 h-20 glass-nav transition-all duration-300 w-full">
      <div className="container mx-auto px-4 h-full flex items-center justify-between">
        {/* Logo Section */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center group cursor-pointer">
            <div className="relative w-8 h-8 mr-3 flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-2xl absolute group-hover:animate-pulse transition-all">
                shield
              </span>
              <div className="absolute inset-0 bg-white/10 blur-md rounded-full group-hover:bg-cyan-500/20 transition-all"></div>
            </div>
            <span className="font-sans font-bold text-lg tracking-tight text-white">
              Vuln
              <span className="text-slate-400 group-hover:text-white transition-colors">
                Scanner
              </span>
            </span>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center p-1 bg-white/5 rounded-full border border-white/5 backdrop-blur-md">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200',
                  pathname === item.href || pathname.startsWith(item.href + '/')
                    ? 'bg-interactive-dark text-white shadow-lg border border-white/10'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                )}
              >
                {item.title}
              </Link>
            ))}
          </nav>
        </div>

        {/* Search Bar (Centered) */}
        <div className="hidden lg:flex flex-1 items-center justify-center px-8">
          <div className="relative group w-full max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="material-symbols-outlined text-slate-500 group-focus-within:text-cyan-400 transition-colors">
                search
              </span>
            </div>
            <input
              type="text"
              placeholder="Search assets..."
              className="w-full pl-10 pr-4 py-2 rounded-full bg-white/5 border border-white/10 text-slate-200 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all placeholder:text-slate-600"
            />
          </div>
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center gap-4">
          <div className="hidden lg:flex items-center gap-2 mr-2">
            <Link href="/projects/new">
              <Button
                variant="ghost"
                size="sm"
                className="text-slate-400 hover:text-white hover:bg-white/10"
              >
                <span className="material-symbols-outlined mr-2 text-lg">folder_open</span>
                New Project
              </Button>
            </Link>
            <Link href="/scans/new">
              <Button
                size="sm"
                className="bg-white text-black hover:bg-gray-200 font-bold shadow-glow hover:shadow-glow-hover transition-all"
              >
                <span className="material-symbols-outlined mr-2 text-lg">radar</span>
                New Scan
              </Button>
            </Link>
          </div>

          <div className="h-6 w-px bg-white/10 mx-1 hidden lg:block"></div>

          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 text-slate-400 hover:text-white hover:bg-white/10 rounded-full"
          >
            <Bell className="h-5 w-5" />
            <span className="sr-only">Notifications</span>
          </Button>

          <div className="h-6 w-px bg-white/10 mx-1"></div>

          <div className="flex items-center gap-3">
            <div className="hidden md:block text-right">
              <p className="text-xs font-medium text-white">Admin</p>
              <p className="text-[10px] text-slate-400 font-mono">Free Plan</p>
            </div>
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 border border-white/20 shadow-glow" />
          </div>

          <form action="/auth/signout" method="post">
            <Button
              variant="ghost"
              size="sm"
              className="ml-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
            >
              <span className="material-symbols-outlined text-lg">logout</span>
            </Button>
          </form>
        </div>
      </div>
    </header>
  );
}
