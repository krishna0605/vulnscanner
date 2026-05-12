import type { Metadata } from 'next';
import { Space_Grotesk, JetBrains_Mono } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import './globals.css';
import { Toaster } from '@/components/toast-provider';
import { ConvexClientProvider } from '@/components/convex-client-provider';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-sans',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
});

export const metadata: Metadata = {
  title: 'VulnScanner - AI Threat Intelligence',
  description: 'Advanced URL Vulnerability Scanning Platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const skipAuthForE2E = process.env.E2E_SKIP_AUTH === 'true';

  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className={`${spaceGrotesk.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        {skipAuthForE2E ? (
          <>
            {children}
            <Toaster />
          </>
        ) : (
          <ClerkProvider>
            <ConvexClientProvider>
              {children}
              <Toaster />
            </ConvexClientProvider>
          </ClerkProvider>
        )}
      </body>
    </html>
  );
}
