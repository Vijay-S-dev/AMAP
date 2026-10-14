import { NextResponse, type NextRequest } from 'next/server';
import {
  decodeTokenPayload,
  isPathAllowedForRoles,
  landingPathForRoles,
} from './shared/auth/routeAccess';

/**
 * Hybrid Control Interface — Edge Route Protection Middleware (§ 7, § 50)
 *
 * Two gates, both enforced BEFORE any protected page renders:
 *
 * 1. Authentication: a structurally valid, unexpired JWT must be present.
 * 2. Authorization: the JWT's roles claim must be admitted to the route
 *    (worker-lifecycle / fleet / admin), mirroring the backend RBAC role
 *    sets. Unauthorized users are redirected to their own role's landing
 *    page — the protected page is never rendered and no protected data is
 *    fetched or leaked during the redirect.
 *
 * IMPORTANT SECURITY BOUNDARY NOTE:
 * This edge middleware performs structural and role-claim gating only to
 * prevent unauthorized UI rendering. It does NOT perform cryptographic HMAC
 * signature verification (to avoid exposing secrets to the edge/frontend
 * runtime). The FastAPI backend remains the authoritative cryptographic
 * security boundary enforcing signature verification, active user status,
 * and RBAC authorization on every API request.
 */

const PROTECTED_PREFIXES = [
  '/worker',
  '/organization',
  '/organisation',
  '/admin',
  '/onboarding',
  '/training',
];

function extractToken(request: NextRequest): string | null {
  let rawToken = request.cookies.get('amap_token')?.value;

  // Strip enclosing quotes that some cookie parsers may include
  if (rawToken && rawToken.startsWith('"') && rawToken.endsWith('"')) {
    rawToken = rawToken.slice(1, -1);
  }

  if (!rawToken) {
    const authHeader = request.headers.get('authorization');
    if (authHeader && authHeader.startsWith('Bearer ')) {
      rawToken = authHeader.substring(7).trim();
    }
  }

  return rawToken || null;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );

  if (isProtected) {
    const rawToken = extractToken(request);

    // Gate 1 — authentication: reject missing, fake, expired, or malformed
    // tokens (no x-amap-authenticated bypass).
    const payload = decodeTokenPayload(rawToken);
    const isUnexpired =
      !!rawToken &&
      !!payload &&
      (!payload.exp || Math.floor(Date.now() / 1000) < (payload.exp as number));

    if (!isUnexpired) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Gate 2 — authorization: the role must be admitted to this route.
    // Mirrors backend RBAC; redirects to the user's own landing page.
    if (!isPathAllowedForRoles(pathname, payload?.roles ?? null)) {
      const landing = new URL(landingPathForRoles(payload?.roles ?? null), request.url);
      return NextResponse.redirect(landing);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/worker/:path*',
    '/organization/:path*',
    '/organisation/:path*',
    '/admin/:path*',
    '/onboarding/:path*',
    '/training/:path*',
  ],
};
