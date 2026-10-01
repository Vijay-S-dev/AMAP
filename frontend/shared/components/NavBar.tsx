'use client';

/**
 * Shared Global Top Navigation Bar (§ 28, § 30)
 * Provides accessible navigation across all AMAP routes, quick language switcher,
 * high contrast toggle, and tenant identity.
 */

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAccessibility } from '@/shared/theme/AccessibilityContext';
import { SUPPORTED_LANGUAGES, SupportedLanguage } from '@/shared/i18n/languages';
import { api } from '@/shared/api/client';

export function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { language, setLanguage, highContrast, setHighContrast, isReady } = useAccessibility();

  // Auth session presence (client-side JWT). Re-checked on every route change
  // so the Logout control appears after login and disappears after logout.
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  React.useEffect(() => {
    setIsAuthenticated(
      typeof window !== 'undefined' && Boolean(window.localStorage.getItem('amap_token'))
    );
  }, [pathname]);

  const handleLogout = () => {
    // Stateless JWT auth: logout = discard the client credentials (token +
    // org context + edge-middleware cookie). Protected routes then redirect
    // to /login via the middleware.
    api.clearAuth();
    setIsAuthenticated(false);
    router.push('/login');
  };

  const navLinks = [
    { href: '/', label: 'Overview', badge: 'Hub' },
    { href: '/login', label: 'Login', badge: 'Auth' },
    { href: '/onboarding', label: 'Onboarding', badge: isReady ? '✓ Ready' : 'Setup' },
    { href: '/training', label: 'Training', badge: '#1042' },
    { href: '/worker', label: 'Worker Station', badge: 'HUD', color: 'var(--worker-cyan)' },
    { href: '/organization', label: 'Fleet & Supervisor', badge: 'Fleet', color: 'var(--org-emerald)' },
    { href: '/admin', label: 'Admin Studio', badge: 'Governance', color: 'var(--admin-purple)' },
  ];

  return (
    <header className="glass-panel" style={{ margin: '1rem 1.5rem', padding: '0.85rem 1.5rem', borderRadius: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', textDecoration: 'none' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #00f2fe 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                color: '#0b0f19',
                fontSize: '1.1rem',
              }}
            >
              HCI
            </div>
            <div>
              <span style={{ fontSize: '0.95rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'white' }}>Hybrid Control Interface</span>
              <span style={{ display: 'block', fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Accessible Multimodal Assembly
              </span>
            </div>
          </Link>
        </div>

        {/* Product Navigation Tabs */}
        <nav aria-label="Main Navigation" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className="btn btn-secondary"
                aria-current={isActive ? 'page' : undefined}
                style={{
                  fontSize: '0.85rem',
                  padding: '0.5rem 0.95rem',
                  minHeight: '48px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  background: isActive ? 'rgba(255, 255, 255, 0.15)' : 'transparent',
                  borderColor: isActive ? 'rgba(255, 255, 255, 0.3)' : 'transparent',
                  color: isActive ? link.color || '#fff' : 'var(--text-secondary)',
                  fontWeight: isActive ? 700 : 500,
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Language Switcher & Accessibility Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Quick Language Dropdown */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
            aria-label="Select Interface Language"
            style={{
              padding: '0.5rem 0.75rem',
              minHeight: '48px',
              borderRadius: '8px',
              background: 'var(--surface-card)',
              color: 'white',
              border: '1px solid var(--surface-glass-border)',
              fontSize: '0.85rem',
              fontWeight: 600,
            }}
          >
            {SUPPORTED_LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.flag} {l.nativeName}
              </option>
            ))}
          </select>

          {/* High Contrast Button */}
          <button
            type="button"
            onClick={() => setHighContrast(!highContrast)}
            className="btn btn-secondary"
            aria-pressed={highContrast}
            aria-label="Toggle High Contrast Mode"
            style={{ fontSize: '0.85rem', padding: '0.5rem 1rem', minHeight: '48px', display: 'inline-flex', alignItems: 'center' }}
          >
            {highContrast ? '👁️ Standard' : '🔲 High Contrast'}
          </button>

          {/* Logout (visible only in an authenticated session) */}
          {isAuthenticated && (
            <button
              type="button"
              onClick={handleLogout}
              className="btn btn-secondary"
              aria-label="Log out of Hybrid Control Interface"
              style={{ fontSize: '0.85rem', padding: '0.5rem 1rem', minHeight: '48px', display: 'inline-flex', alignItems: 'center' }}
            >
              🚪 Logout
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
