import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ASR Data Enrichment - SNOW Ticket Quality',
  description: 'AI-powered ServiceNow ticket enrichment for automation enablement',
  keywords: ['ServiceNow', 'SNOW', 'Ticket Quality', 'AI Enrichment', 'ASR', 'Automation']
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
