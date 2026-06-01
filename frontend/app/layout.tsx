import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import './globals.css'

export const metadata: Metadata = {
  title: 'CreatorJoy | RAG Video Analyzer',
  description:
    'Compare YouTube and Instagram videos with AI-powered RAG analysis, engagement insights, hook analysis, and improvement suggestions.',
  applicationName: 'CreatorJoy',
  authors: [{ name: 'Asad Shaikh' }],
  keywords: [
    'CreatorJoy',
    'RAG',
    'video analyzer',
    'YouTube analysis',
    'Instagram analysis',
    'AI content analysis',
  ],
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="app-shell">{children}</main>
      </body>
    </html>
  )
}