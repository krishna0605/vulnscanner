import { Header } from '@/components/layout/header';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-background-dark text-white font-sans selection:bg-cyan-500/30">
      <div className="fixed inset-0 w-full h-full -z-30 bg-background-dark"></div>
      <div className="fixed inset-0 w-full h-full -z-20 bg-mesh-gradient opacity-60"></div>
      <Header />
      <main className="flex-1 container mx-auto p-6 md:p-8">{children}</main>
    </div>
  );
}
