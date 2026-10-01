/**
 * Role-based navigation & route-access policy (single source of truth).
 *
 * Used by THREE consumers so the navbar, the edge middleware and the tests
 * can never drift apart:
 *   - frontend/shared/components/NavBar.tsx   (role-aware navigation)
 *   - frontend/middleware.ts                  (route guards for direct URLs)
 *   - frontend/tests/route-access.test.ts     (role → route matrix tests)
 *
 * Edge-safe: no DOM, no localStorage, no Node APIs.
 *
 * SECURITY BOUNDARY: this mirrors the BACKEND RBAC role sets
 * (backend/routes/supervisor.py: supervisor, manager, admin,
 * organization_admin, superadmin; backend/routes/admin.py: admin,
 * super_admin / organization_admin). The frontend guard only prevents
 * UNAUTHORIZED UI RENDERING; the FastAPI backend remains the authoritative
 * cryptographic security boundary on every API request.
 */

/** Roles admitted to supervisor/fleet routes (mirrors the /supervisor router). */
export const FLEET_ROLES = [
  'supervisor',
  'manager',
  'admin',
  'organization_admin',
  'superadmin',
  'super_admin',
] as const;

/** Roles admitted to admin studio routes (mirrors the /admin router). */
export const ADMIN_ROLES = [
  'admin',
  'organization_admin',
  'superadmin',
  'super_admin',
] as const;

/** Worker-lifecycle routes (worker station, onboarding, training). */
const WORKER_PREFIXES = ['/worker', '/onboarding', '/training'] as const;

/** Supervisor fleet routes (both spellings are routed). */
const FLEET_PREFIXES = ['/organization', '/organisation'] as const;

/** Admin studio routes. */
const ADMIN_PREFIXES = ['/admin'] as const;

export interface NavItem {
  href: string;
  label: string;
  badge?: string;
  color?: string;
}

export interface TokenPayload {
  roles: string[];
  exp?: number;
  sub?: string;
  organization_id?: string;
}

/** Decode a JWT payload WITHOUT verification (UI gating only). */
export function decodeTokenPayload(token: string | null | undefined): TokenPayload | null {
  if (!token || typeof token !== 'string') return null;
  if (token.startsWith('demo_token')) return null;
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  try {
    let base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) base64 += '=';
    const payload = JSON.parse(atob(base64));
    if (!payload || typeof payload !== 'object') return null;
    return {
      roles: Array.isArray(payload.roles) ? payload.roles.map(String) : [],
      exp: typeof payload.exp === 'number' ? payload.exp : undefined,
      sub: payload.sub,
      organization_id: payload.organization_id,
    };
  } catch {
    return null;
  }
}

/** True when the decoded payload exists and is not expired. */
export function isPayloadActive(payload: TokenPayload | null): payload is TokenPayload {
  if (!payload) return false;
  if (payload.exp && typeof payload.exp === 'number') {
    return Math.floor(Date.now() / 1000) < payload.exp;
  }
  return true;
}

function hasAny(roles: string[] | null | undefined, allowed: readonly string[]): boolean {
  if (!roles || roles.length === 0) return false;
  return roles.some((r) => (allowed as readonly string[]).includes(r));
}

export function isWorker(roles: string[] | null | undefined): boolean {
  return hasAny(roles, ['worker']);
}

export function isFleetRole(roles: string[] | null | undefined): boolean {
  return hasAny(roles, FLEET_ROLES);
}

export function isAdminRole(roles: string[] | null | undefined): boolean {
  return hasAny(roles, ADMIN_ROLES);
}

function matchesPrefix(pathname: string, prefixes: readonly string[]): boolean {
  return prefixes.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

/**
 * Authoritative frontend route guard.
 * Returns true when a user with these roles may RENDER this path.
 */
export function isPathAllowedForRoles(pathname: string, roles: string[] | null | undefined): boolean {
  if (matchesPrefix(pathname, WORKER_PREFIXES)) {
    // Worker lifecycle routes: workers only.
    return isWorker(roles);
  }
  if (matchesPrefix(pathname, FLEET_PREFIXES)) {
    return isFleetRole(roles);
  }
  if (matchesPrefix(pathname, ADMIN_PREFIXES)) {
    return isAdminRole(roles);
  }
  // Public routes (/, /login) are always allowed.
  return true;
}

/** Landing page for a user with these roles (used for unauthorized redirects). */
export function landingPathForRoles(roles: string[] | null | undefined): string {
  if (isAdminRole(roles)) return '/admin';
  if (isFleetRole(roles)) return '/organization';
  if (isWorker(roles)) return '/worker';
  return '/login';
}

/**
 * Role-aware navigation items.
 *  - Unauthenticated: Overview + Login only (no authenticated destinations).
 *  - Worker: Overview, Onboarding, Training, Worker Station.
 *  - Supervisor/Manager: Overview, Fleet & Supervisor.
 *  - Admin/Org Admin: Overview, Fleet & Supervisor, Admin Studio.
 */
export function navLinksForRoles(roles: string[] | null | undefined): NavItem[] {
  const links: NavItem[] = [{ href: '/', label: 'Overview', badge: 'Hub' }];

  if (!roles || roles.length === 0) {
    links.push({ href: '/login', label: 'Login', badge: 'Auth' });
    return links;
  }

  if (isWorker(roles)) {
    links.push(
      { href: '/onboarding', label: 'Onboarding', badge: 'Setup' },
      { href: '/training', label: 'Training', badge: '#1042' },
      { href: '/worker', label: 'Worker Station', badge: 'HUD', color: 'var(--worker-cyan)' }
    );
  }

  if (isFleetRole(roles)) {
    links.push({
      href: '/organization',
      label: 'Fleet & Supervisor',
      badge: 'Fleet',
      color: 'var(--org-emerald)',
    });
  }

  if (isAdminRole(roles)) {
    links.push({
      href: '/admin',
      label: 'Admin Studio',
      badge: 'Governance',
      color: 'var(--admin-purple)',
    });
  }

  return links;
}
