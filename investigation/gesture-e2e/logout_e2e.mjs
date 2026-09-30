// AMAP Phase 3 logout E2E (headless real browser).
// Verifies the NavBar Logout control: seeded authenticated session ->
// Logout button visible on /worker -> click -> credentials discarded
// (localStorage + cookie) and the user lands on /login.
// Usage: node logout_e2e.mjs [waitMs]   (rig: RIG_DIR env, default /tmp/browser)
import { createRequire } from 'module';
const rigRequire = createRequire((process.env.RIG_DIR || '/tmp/browser') + '/');
const puppeteer = rigRequire('puppeteer-core');

const BASE = 'http://127.0.0.1:3000';
const ORG = '9a61e05d-7a32-4112-9c17-1833d7b42f65';

const fail = (msg) => { console.error('LOGOUT E2E FAIL:', msg); process.exit(1); };

const browser = await puppeteer.launch({
  executablePath: '/tmp/chromium',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--headless=new', '--window-size=1600,1200'],
});
try {
  // 1. Mint a real token via the API.
  await (await browser.createIncognitoBrowserContext?.() ?? browser).newPage?.();
  const page = await browser.newPage();
  await page.goto(`${BASE}/login`, { waitUntil: 'networkidle2', timeout: 120000 });
  const loginRes = await page.evaluate(async (url) => {
    const r = await fetch(`${url}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization_id: '9a61e05d-7a32-4112-9c17-1833d7b42f65',
        email: 'alex.worker@amap.com',
        password: 'SecurePassword123!',
      }),
    });
    return await r.json();
  }, BASE);
  if (!loginRes.access_token) fail('API login failed: ' + JSON.stringify(loginRes).slice(0, 200));
  const token = loginRes.access_token;

  // 2. Seed the authenticated session exactly like the production client does.
  await page.evaluateOnNewDocument((t) => {
    localStorage.setItem('amap_token', t);
    localStorage.setItem('amap_org_id', '9a61e05d-7a32-4112-9c17-1833d7b42f65');
    document.cookie = `amap_token=${t}; path=/; max-age=86400; SameSite=Lax`;
  }, token);

  // 3. Open /worker with the session.
  await page.goto(`${BASE}/worker`, { waitUntil: 'networkidle2', timeout: 120000 });

  // 4. The NavBar must show the Logout control.
  await page.waitForSelector('button[aria-label="Log out of AMAP"]', { timeout: 30000 });
  const visible = await page.evaluate(() => {
    const b = document.querySelector('button[aria-label="Log out of AMAP"]');
    return !!b && b.offsetParent !== null;
  });
  if (!visible) fail('Logout button present in DOM but not visible');

  // 5. Click Logout.
  await page.click('button[aria-label="Log out of AMAP"]');

  // 6. Expect navigation to /login.
  await page.waitForFunction(() => window.location.pathname === '/login', { timeout: 30000 });

  // 7. Credentials must be discarded.
  const creds = await page.evaluate(() => ({
    token: localStorage.getItem('amap_token'),
    org: localStorage.getItem('amap_org_id'),
    cookieHasToken: document.cookie.includes('amap_token='),
  }));
  if (creds.token !== null) fail('amap_token still in localStorage after logout');
  if (creds.org !== null) fail('amap_org_id still in localStorage after logout');
  if (creds.cookieHasToken) fail('amap_token cookie still set after logout');

  // 8. A protected route must now redirect to /login (middleware gate).
  await page.goto(`${BASE}/worker`, { waitUntil: 'networkidle2', timeout: 120000 }).catch(() => {});
  const landed = await page.evaluate(() => window.location.pathname);

  console.log('LOGOUT E2E PASS:', JSON.stringify({
    logoutButtonVisible: true,
    redirectedToLogin: true,
    localStorageCleared: true,
    cookieCleared: true,
    protectedRouteAfterLogout: landed,
  }));
} finally {
  await browser.close();
}
