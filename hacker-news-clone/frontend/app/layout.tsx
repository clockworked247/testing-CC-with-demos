import type { Metadata } from 'next'
import './globals.css'
import Header from '@/components/layout/Header'
import { AuthProvider } from '@/components/providers/AuthProvider'

export const metadata: Metadata = {
  title: 'Hacker News Clone',
  description: 'A full-featured Hacker News clone built with Next.js',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex-1 container mx-auto max-w-6xl px-4 py-4">
              {children}
            </main>
            <footer className="bg-gray-800 text-white py-4 text-center text-sm">
              <p>Hacker News Clone &copy; {new Date().getFullYear()}</p>
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}
