import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'EPV Dashboard',
  description: 'Equity Valuation Platform',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="bg-gray-900 text-white px-6 py-3 flex gap-4">
          <a href="/" className="font-semibold">Home</a>
          <a href="/api-status">API Status</a>
          <a href="/analysis">Analysis</a>
          <a href="/batch">Batch</a>
          <a href="/risk">Risk</a>
        </header>
        {children}
      </body>
    </html>
  )
}
