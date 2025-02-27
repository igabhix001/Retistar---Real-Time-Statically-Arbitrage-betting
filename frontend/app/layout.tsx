import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Nav } from '@/components/nav'
const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'RETISTAR - REAL TIME STATISTICAL ARBITRAGE BETTING',
  description: 'Bet on sports with skill and strategy',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-white text-black min-h-screen flex flex-col`}>
        <Nav />
        <main className="flex-grow">{children}</main>
      </body>
    </html>
  );
}

