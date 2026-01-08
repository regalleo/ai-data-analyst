import type { Metadata } from 'next';
import { AuthProvider } from '@/hooks/useAuth';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'AI Data Analyst',
  description: 'Multi-tenant AI-powered data analysis platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-950">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}

