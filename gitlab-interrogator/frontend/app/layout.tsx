import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Providers from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'GitLab Interrogator - AI Scrum Master',
  description: 'AI-powered GitLab Agile workflow automation for story creation, sprint analysis, release notes, and epic categorization',
  keywords: ['GitLab', 'Agile', 'Scrum', 'AI', 'Automation', 'User Stories', 'Sprint Summary', 'Release Notes'],
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
