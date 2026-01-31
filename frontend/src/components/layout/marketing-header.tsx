import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Shield } from 'lucide-react';

export function MarketingHeader() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6 lg:px-12">
      <div className="flex items-center gap-2">
        <Shield className="h-6 w-6 text-primary" />
        <span className="text-lg font-bold">VulnScanner AI</span>
      </div>
      <nav className="hidden gap-6 md:flex">
        <Link href="/" className="text-sm font-medium hover:underline">
          Features
        </Link>
        <Link href="/pricing" className="text-sm font-medium hover:underline">
          Pricing
        </Link>
        <Link href="/about" className="text-sm font-medium hover:underline">
          About
        </Link>
      </nav>
      <div className="flex items-center gap-4">
        <Link href="/login">
          <Button variant="ghost">Log in</Button>
        </Link>
        <Link href="/signup">
          <Button>Get Standard</Button>
        </Link>
      </div>
    </header>
  );
}
