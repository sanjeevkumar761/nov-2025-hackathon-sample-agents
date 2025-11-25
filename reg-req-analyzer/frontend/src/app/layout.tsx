import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Regulatory Requirements Analyzer',
  description: 'AI-powered regulatory document analysis for compliance teams',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen p-8">
          <header className="mb-8">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-4xl font-bold text-white mb-2">
                Regulatory Requirements Analyzer
              </h1>
              <p className="text-white/90 text-lg">
                AI-powered extraction and analysis of Laws, Rules, and Regulations
              </p>
            </div>
          </header>
          <main className="max-w-7xl mx-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
