import type { Metadata } from 'next';
import { I18nProvider } from '@/lib/i18n';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ToastContainer from '@/components/ToastContainer';
import './globals.css';

export const metadata: Metadata = {
  title: 'PetPal — Premium Desktop Pet Creator',
  description: 'Turn your pet photos into exquisite desktop companions with AI. Create personalized desktop pets and animated sticker packs.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased min-h-screen flex flex-col bg-surface">
        <I18nProvider>
          <Header />
          <main className="flex-1 pt-20">
            {children}
          </main>
          <Footer />
          <ToastContainer />
        </I18nProvider>
      </body>
    </html>
  );
}
