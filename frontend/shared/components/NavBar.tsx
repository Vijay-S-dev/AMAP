'use client';

/**
 * Shared Global Top Navigation Bar (§ 28, § 30)
 * Role-aware navigation for Hybrid Control Interface: the visible links are
 * generated from the authenticated user's roles (single source of truth:
 * shared/auth/routeAccess), so a Worker never sees or reaches supervisor or
 * admin destinations. Quick language switcher, high contrast toggle, and
 * tenant identity are shared across roles.
 *
 * Flash prevention: navigation renders only after the auth/role state has
 * been resolved from the stored JWT (a "resolving" placeholder is shown for
 * at most the first client frame) — role-specific links are never shown to
 * the wrong role.
 */

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAccessibility } from '@/shared/theme/AccessibilityContext';
import { SUPPORTED_LANGUAGES, SupportedLanguage } from '@/shared/i18n/languages';
import { api } from '@/shared/api/client';
import {
  decodeTokenPayload,
  isNavLinkActive,
  isPayloadActive,
  navLinksForRoles,
} from '@/shared/auth/routeAccess';

type AuthNavState =
  | { status: 'resolving' }
  | { status: 'ready'; roles: string[] | null };

export function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { language, setLanguage, highContrast, setHighContrast } = useAccessibility();

  // Auth session + role resolution (client-side JWT). Re-resolved on every
  // route change so the navbar updates after login / logout / role switch.
  const [authNav, setAuthNav] = React.useState<AuthNavState>({ status: 'resolving' });
  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    const payload = decodeTokenPayload(window.localStorage.getItem('amap_token'));
    setAuthNav({ status: 'ready', roles: isPayloadActive(payload) ? payload.roles : null });
  }, [pathname]);

  const handleLogout = () => {
    // Stateless JWT auth: logout = discard the client credentials (token +
    // org context + edge-middleware cookie). Protected routes then redirect
    // to /login via the middleware.
    api.clearAuth();
    setAuthNav({ status: 'ready', roles: null });
    router.push('/login');
  };

  const roles = authNav.status === 'ready' ? authNav.roles : null;
  // Role-aware links (single source of truth with the middleware guard).
  const navLinks = navLinksForRoles(roles);

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
                Multimodal Industrial Workflows
              </span>
            </div>
          </Link>
        </div>

        {/* Role-aware Product Navigation Tabs (rendered after role resolution) */}
        <nav aria-label="Main Navigation" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap', minHeight: '48px' }}>
          {authNav.status === 'resolving' ? (
            <span aria-live="polite" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0 0.95rem' }}>
              Loading navigation…
            </span>
          ) : (
            navLinks.map((link) => {
              const isActive = isNavLinkActive(link.href, pathname);
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
            })
          )}
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
          {authNav.status === 'ready' && authNav.roles && (
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
