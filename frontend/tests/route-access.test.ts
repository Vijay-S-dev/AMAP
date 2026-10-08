/**
 * Role-based route access + navigation tests (frontend/tests/route-access.test.ts)
 *
 * Focused tests for the navigation/authorization matrix shared by the navbar
 * and the edge middleware (shared/auth/routeAccess):
 *  - Worker sees/reaches only worker-lifecycle routes; fleet & admin are
 *    denied by direct URL.
 *  - Supervisor sees/reaches fleet routes; admin studio is denied.
 *  - Admin sees/reaches fleet + admin routes.
 *  - Unauthenticated users get no authenticated destinations in the navbar.
 *  - Expired or malformed tokens resolve to the unauthenticated state.
 *  - Current-page highlighting: exact root for Overview, prefix-aware for
 *    section tabs (sub-routes keep their tab highlighted).
 *
 * Run via: node scripts/run-engine-tests.mjs  (compiles with tsc first)
 */

import {
  decodeTokenPayload,
  isPathAllowedForRoles,
  isNavLinkActive,
  landingPathForRoles,
  navLinksForRoles,
  isPayloadActive,
} from '../shared/auth/routeAccess';

// ---------------------------------------------------------------------------
// Minimal test framework (same style as gesture-engine.test.ts)
// ---------------------------------------------------------------------------
let passed = 0;
let failed = 0;
const failures: string[] = [];

function assert(condition: unknown, message: string): void {
  if (condition) {
    passed += 1;
  } else {
    failed += 1;
    failures.push(message);
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a structurally valid (unsigned) JWT with the given claims. */
function fakeJwt(claims: Record<string, unknown>): string {
  const b64 = (obj: unknown) =>
    btoa(JSON.stringify(obj)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  return `${b64({ alg: 'HS256', typ: 'JWT' })}.${b64(claims)}.sig`;
}

const WORKER = ['worker'];
const SUPERVISOR = ['supervisor'];
const ADMIN = ['admin'];
const ORG_ADMIN = ['organization_admin'];

// ---------------------------------------------------------------------------
// 1. Route guard matrix
// ---------------------------------------------------------------------------
function testRouteMatrix(): void {
  const cases: Array<{ role: string; roles: string[] | null; path: string; allowed: boolean }> = [
    // Worker
    { role: 'worker', roles: WORKER, path: '/worker', allowed: true },
    { role: 'worker', roles: WORKER, path: '/worker/detail', allowed: true }, // prefix-based guard
    { role: 'worker', roles: WORKER, path: '/training', allowed: true },
    { role: 'worker', roles: WORKER, path: '/onboarding/language', allowed: true },
    { role: 'worker', roles: WORKER, path: '/organization', allowed: false },
    { role: 'worker', roles: WORKER, path: '/organisation', allowed: false },
    { role: 'worker', roles: WORKER, path: '/admin', allowed: false },
    { role: 'worker', roles: WORKER, path: '/admin/users', allowed: false },
    // Supervisor
    { role: 'supervisor', roles: SUPERVISOR, path: '/organization', allowed: true },
    { role: 'supervisor', roles: SUPERVISOR, path: '/organisation', allowed: true },
    { role: 'supervisor', roles: SUPERVISOR, path: '/admin', allowed: false },
    { role: 'supervisor', roles: SUPERVISOR, path: '/admin/configs', allowed: false },
    { role: 'supervisor', roles: SUPERVISOR, path: '/worker', allowed: false },
    { role: 'supervisor', roles: SUPERVISOR, path: '/training', allowed: false },
    // Admin
    { role: 'admin', roles: ADMIN, path: '/admin', allowed: true },
    { role: 'admin', roles: ADMIN, path: '/organization', allowed: true },
    { role: 'admin', roles: ADMIN, path: '/worker', allowed: false },
    { role: 'org_admin', roles: ORG_ADMIN, path: '/admin', allowed: true },
    { role: 'org_admin', roles: ORG_ADMIN, path: '/organization', allowed: true },
    // Unauthenticated
    { role: 'anonymous', roles: null, path: '/worker', allowed: false },
    { role: 'anonymous', roles: null, path: '/organization', allowed: false },
    { role: 'anonymous', roles: null, path: '/admin', allowed: false },
    { role: 'anonymous', roles: null, path: '/', allowed: true },
    { role: 'anonymous', roles: null, path: '/login', allowed: true },
  ];

  for (const c of cases) {
    assert(
      isPathAllowedForRoles(c.path, c.roles) === c.allowed,
      `${c.role} ${c.allowed ? 'must be allowed' : 'must be DENIED'} at ${c.path}`
    );
  }
}

// ---------------------------------------------------------------------------
// 2. Navbar matrix
// ---------------------------------------------------------------------------
function testNavMatrix(): void {
  const labels = (roles: string[] | null) => navLinksForRoles(roles).map((l) => l.label);

  // Unauthenticated: no authenticated destinations exposed.
  const anon = labels(null);
  assert(anon.includes('Overview') && anon.includes('Login'), 'anonymous nav: Overview + Login');
  assert(
    !anon.includes('Worker Station') && !anon.includes('Fleet & Supervisor') && !anon.includes('Admin Studio'),
    'anonymous nav must not expose authenticated destinations'
  );

  // Worker
  const worker = labels(WORKER);
  assert(worker.includes('Worker Station') && worker.includes('Training'), 'worker nav: station + training');
  assert(
    !worker.includes('Fleet & Supervisor') && !worker.includes('Admin Studio'),
    'worker nav must NOT contain Fleet & Supervisor or Admin Studio'
  );

  // Supervisor
  const sup = labels(SUPERVISOR);
  assert(sup.includes('Fleet & Supervisor'), 'supervisor nav: Fleet & Supervisor');
  assert(!sup.includes('Admin Studio'), 'supervisor nav must NOT contain Admin Studio');
  assert(!sup.includes('Worker Station'), 'supervisor nav must NOT contain Worker Station');

  // Admin
  const adm = labels(ADMIN);
  assert(adm.includes('Admin Studio') && adm.includes('Fleet & Supervisor'), 'admin nav: Admin Studio + Fleet');
}

// ---------------------------------------------------------------------------
// 3. Landing pages for unauthorized redirects
// ---------------------------------------------------------------------------
function testLandingPaths(): void {
  assert(landingPathForRoles(WORKER) === '/worker', 'worker landing = /worker');
  assert(landingPathForRoles(SUPERVISOR) === '/organization', 'supervisor landing = /organization');
  assert(landingPathForRoles(ADMIN) === '/admin', 'admin landing = /admin');
  assert(landingPathForRoles(null) === '/login', 'anonymous landing = /login');
}

// ---------------------------------------------------------------------------
// 4. Token decoding (auth + role resolution)
// ---------------------------------------------------------------------------
function testTokenDecoding(): void {
  const nowSec = Math.floor(Date.now() / 1000);
  const good = decodeTokenPayload(fakeJwt({ roles: WORKER, exp: nowSec + 3600 }));
  assert(good !== null && good.roles[0] === 'worker', 'valid JWT decodes to worker role');
  assert(isPayloadActive(good), 'unexpired payload is active');

  const expired = decodeTokenPayload(fakeJwt({ roles: WORKER, exp: nowSec - 10 }));
  assert(expired !== null && !isPayloadActive(expired), 'expired payload is inactive');

  assert(decodeTokenPayload(null) === null, 'null token rejected');
  assert(decodeTokenPayload('demo_token_123') === null, 'fake demo token rejected');
  assert(decodeTokenPayload('not.a.jwt') === null, 'malformed token rejected');
  assert(decodeTokenPayload('a.b.c.d') === null, 'wrong segment count rejected');

  const noRoles = decodeTokenPayload(fakeJwt({ exp: nowSec + 3600 }));
  assert(noRoles !== null && noRoles.roles.length === 0, 'token without roles -> unauthenticated nav');
  assert(!isPathAllowedForRoles('/worker', noRoles!.roles), 'roleless token denied at /worker');
}

// ---------------------------------------------------------------------------
// Run
// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// 5. Current-page highlighting (navbar aria-current)
// ---------------------------------------------------------------------------
function testActiveLinkHighlighting(): void {
  const cases: Array<{ href: string; pathname: string; active: boolean; note?: string }> = [
    { href: '/', pathname: '/', active: true },
    { href: '/', pathname: '/worker', active: false, note: 'Overview only active on exact root' },
    { href: '/worker', pathname: '/worker', active: true },
    { href: '/worker', pathname: '/worker/detail', active: true, note: 'sub-route highlights its tab' },
    { href: '/onboarding', pathname: '/onboarding/language', active: true, note: 'sub-route highlights its tab' },
    { href: '/training', pathname: '/training/safety', active: true, note: 'sub-route highlights its tab' },
    { href: '/organization', pathname: '/organization/workers', active: true, note: 'sub-route highlights its tab' },
    { href: '/admin', pathname: '/admin/users', active: true, note: 'sub-route highlights its tab' },
    { href: '/worker', pathname: '/workerly', active: false, note: 'no false prefix match' },
    { href: '/worker', pathname: '/training', active: false, note: 'sibling tab not active' },
    { href: '/organization', pathname: '/admin', active: false, note: 'sibling tab not active' },
  ];
  for (const c of cases) {
    assert(
      isNavLinkActive(c.href, c.pathname) === c.active,
      `isNavLinkActive(${JSON.stringify(c.href)}, ${JSON.stringify(c.pathname)}) should be ${c.active}${c.note ? ` (${c.note})` : ''}`
    );
  }
}

testRouteMatrix();
testNavMatrix();
testLandingPaths();
testTokenDecoding();
testActiveLinkHighlighting();

console.log('=========================================================');
if (failed > 0) {
  console.log(`  route-access tests: ${passed} passed, ${failed} failed`);
  console.log('\nFailures:');
  for (const failure of failures) console.log(`  - ${failure}`);
  process.exit(1);
} else {
  console.log(`  route-access tests: ${passed} passed, 0 failed`);
  console.log('=========================================================');
}
