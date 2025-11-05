'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';

export default function Header() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuthStore();

  const navItems = [
    { href: '/', label: 'top', active: pathname === '/' },
    { href: '/new', label: 'new', active: pathname === '/new' },
    { href: '/best', label: 'best', active: pathname === '/best' },
    { href: '/ask', label: 'ask', active: pathname === '/ask' },
    { href: '/show', label: 'show', active: pathname === '/show' },
    { href: '/jobs', label: 'jobs', active: pathname === '/jobs' },
  ];

  return (
    <header className="bg-hn-orange border-b-2 border-orange-700">
      <div className="container mx-auto max-w-6xl px-4">
        <div className="flex items-center h-12">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 mr-4">
            <div className="w-4 h-4 bg-white border border-white"></div>
            <span className="text-white font-bold text-sm">Hacker News</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-3 text-sm flex-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`text-gray-900 hover:underline ${
                  item.active ? 'font-bold' : ''
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Auth Section */}
          <div className="flex items-center space-x-3 text-sm">
            {isAuthenticated && user ? (
              <>
                <Link
                  href="/submit"
                  className="text-gray-900 hover:underline"
                >
                  submit
                </Link>
                <Link
                  href={`/user/${user.username}`}
                  className="text-gray-900 hover:underline"
                >
                  {user.username} ({user.karma})
                </Link>
                <button
                  onClick={logout}
                  className="text-gray-900 hover:underline"
                >
                  logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-gray-900 hover:underline"
                >
                  login
                </Link>
                <Link
                  href="/register"
                  className="text-gray-900 hover:underline"
                >
                  register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
