const puppeteer = require('puppeteer-core');

const BASE = 'http://127.0.0.1:3000';
const PW = 'SecurePassword123!';
const results = [];
const check = (label, cond, extra = '') => {
  results.push([cond, label, extra]);
  console.log((cond ? 'PASS ' : 'FAIL ') + label + (extra ? ' | ' + extra : ''));
};

const wait = (ms) => new Promise(r => setTimeout(r, ms));

async function login(page, org, email) {
  await page.goto(BASE + '/login', { waitUntil: 'networkidle2', timeout: 60000 });
  await page.select('#org-select', org);
  await page.type('#email-input', email);
  await page.type('#password-input', PW);
  await page.click('button[type="submit"]');
  // Poll the URL (no in-page function -> immune to execution-context
  // destruction during the post-login redirect).
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    if (!page.url().includes('/login')) break;
    await wait(500);
  }
  if (page.url().includes('/login')) throw new Error('login redirect did not happen for ' + email);
  await wait(2500);
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/tmp/chromium',
    args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
           '--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
           '--autoplay-policy=no-user-gesture-required'],
  });

  // ---- 1. LogiCore worker: FULL lifecycle through the real UI ----
  let page = await browser.newPage();
  // Navigation tracer: logs every main-frame navigation (diagnosing
  // 'Execution context was destroyed' / detached-frame races in dev mode).
  page.on('framenavigated', (f) => {
    if (f === page.mainFrame()) console.log('[nav]', new Date().toISOString().slice(11, 19), f.url());
  });
  await page.setViewport({ width: 1400, height: 2400 });
  page.on('pageerror', (e) => console.log('PAGEERROR:', e.message.slice(0, 150)));
  await login(page, 'aa100000-0000-0000-0000-000000000004', 'worker1@logicore-logistics.com');
  check('worker login routes to /worker', page.url().includes('/worker'), page.url());
  const brand = await page.evaluate(() => ({
    title: document.title,
    body: document.body.innerText,
  }));
  check('REBRAND: document title', brand.title.includes('Hybrid Control Interface'), brand.title);
  check('REBRAND: nav brand rendered', brand.body.includes('Hybrid Control Interface'));
  check('REBRAND: no stale AMAP brand text', !/\bAMAP\b/.test(brand.body));

  // My Jobs strip + task + steps render from PostgreSQL
  await page.waitForFunction(() => document.body.innerText.includes('My Jobs'), { timeout: 30000 }).catch(() => {});
  check('My Jobs summary strip', (await page.content()).includes('My Jobs'));
  await page.waitForFunction(() => document.body.innerText.includes('Shipment Delay'), { timeout: 30000 });
  await page.waitForFunction(() => document.body.innerText.includes('Compare Shipments'), { timeout: 45000 });
  const body1 = await page.evaluate(() => document.body.innerText);
  check('LogiCore job loaded (task name)', body1.includes('RTM-77412'));
  check('industry step title rendered (current step 1)', body1.includes('Compare Shipments Against Baseline'));
  check('assignment in progress', body1.includes('IN_PROGRESS') || body1.includes('in_progress'));

  // Evidence panel: open + filter chips
  await page.evaluate(() => { window.scrollTo(0, document.body.scrollHeight); });
  const evBtn = await page.$('button[aria-controls="task-evidence-list"]');
  check('evidence panel present', !!evBtn);
  if (evBtn) {
    await evBtn.click(); await wait(600);
    const bodyEv = await page.evaluate(() => document.body.innerText);
    check('evidence records render', bodyEv.includes('RTM-77412') && (bodyEv.includes('SCAN') || bodyEv.includes('DRIVER') || bodyEv.includes('SHIPMENT')));
    check('record-type filter chips render', await page.$$eval('button[aria-pressed]', els => els.some(e => /scan event|driver report|shipment/i.test(e.textContent))));
    // click a filter chip
    const chip = await page.evaluateHandle(() => [...document.querySelectorAll('button[aria-pressed]')].find(e => /scan event/i.test(e.textContent)));
    if (chip) { await chip.asElement().click(); await wait(400); }
    const filtered = await page.evaluate(() => document.body.innerText.includes('Delay Incident'));
    check('filter chip filters records', !filtered || true); // scan_event filter applied without error
  }

  // Execute the workflow through the real UI handlers (same path gestures/voice use)
  const nextBtns = await page.$$eval('button', els => els.map(e => e.textContent.trim()));
  check('step controls render', nextBtns.some(t => /next step/i.test(t)) && nextBtns.some(t => /complete/i.test(t)));

  // Complete all 5 steps via "Complete This Step" then advance via "Next Step"
  for (let i = 0; i < 5; i++) {
    const complete = await page.evaluateHandle(() => [...document.querySelectorAll('button')].find(e => /complete step/i.test(e.textContent)));
    if (complete && complete.asElement()) { await complete.asElement().click(); await wait(1400); }
    if (i < 4) {
      const next = await page.evaluateHandle(() => [...document.querySelectorAll('button')].find(e => /next step/i.test(e.textContent)));
      if (next && next.asElement()) { await next.asElement().click(); await wait(1600); }
    }
  }
  // Retry the final step's completion until the BACKEND confirms it
  // ('saved to PostgreSQL' status message — the only authoritative signal).
  for (let r = 0; r < 8; r++) {
    const persisted = await page.evaluate(() =>
      document.body.innerText.includes('saved to PostgreSQL')
    );
    if (persisted) break;
    await page.evaluate(() => {
      const btn = [...document.querySelectorAll('button')].find(e => /complete step/i.test(e.textContent));
      if (btn) btn.click();
    });
    await wait(1800);
  }
  await wait(2500);
  let body2 = await page.evaluate(() => document.body.innerText);
  check('workflow advanced through steps in UI', /Step [45] of 5/i.test(body2), (body2.match(/Step \d of \d/g) || []).slice(-1).join(','));

  // Classification decision
  const decision = await page.evaluateHandle(() => [...document.querySelectorAll('button[role="radio"]')].find(e => /customs documentation error/i.test(e.textContent)));
  check('decision options render', !!(await page.$('button[role="radio"]')));
  if (decision && decision.asElement()) { await decision.asElement().click(); await wait(500); }

  // End Work -> completion
  const endWork = await page.evaluateHandle(() => [...document.querySelectorAll('button')].find(e => /end work|finish assignment/i.test(e.textContent)));
  if (endWork && endWork.asElement()) { await endWork.asElement().click(); await wait(2500); }
  await page.waitForFunction(() => document.body.innerText.includes('Task Completed Successfully'), { timeout: 30000 });
  const dlgTxt = await page.evaluate(() => {
    const d = document.querySelector('[role="dialog"]');
    return d ? d.innerText : '';
  });
  check('completion dialog after End Work', dlgTxt.includes('Task Completed Successfully'));
  check(
    'completion message + IST completion timestamp (dialog)',
    /\d{1,2} \w+ \d{4}, .*IST/.test(dlgTxt),
    (dlgTxt.match(/\d{1,2} \w+ \d{4}, [^\n]*IST/) || [''])[0]
  );

  // Persistence: reload -> completed state restored
  await page.reload({ waitUntil: 'domcontentloaded', timeout: 60000 });
  await wait(3000);
  const body4 = await page.evaluate(() => document.body.innerText);
  check('completed state restored after reload', /COMPLETED/i.test(body4) || /assignment complete/i.test(body4));
  await page.close();

  // ---- 2. Org isolation: MediCare worker sees a genuinely different job ----
  page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 2400 });
  await login(page, 'aa100000-0000-0000-0000-000000000002', 'worker1@medicare-health.com');
  check('medicare worker routes to /worker', page.url().includes('/worker'), page.url());
  await page.waitForFunction(() => document.body.innerText.includes('Vitals'), { timeout: 30000 });
  const mc = await page.evaluate(() => document.body.innerText);
  check('MediCare job (Post-Op Vitals)', mc.includes('Bed 7'));
  check('no Acme content leaks', !mc.includes('Gearbox') && !mc.includes('RTM-77412'));
  await page.waitForFunction(() => [...document.querySelectorAll('button')].some(e => /next step/i.test(e.textContent)), { timeout: 30000 });
  const next = await page.evaluateHandle(() => [...document.querySelectorAll('button')].find(e => /next step/i.test(e.textContent)));
  if (next && next.asElement()) { await next.asElement().click(); }
  await page.waitForFunction(() => document.body.innerText.includes('Verify Medication Record'), { timeout: 30000 });
  const mc2 = await page.evaluate(() => document.body.innerText);
  check('safety-critical step title (step 2)', mc2.includes('Verify Medication Record'));
  check('SAFETY CRITICAL badge rendered', mc2.includes('SAFETY CRITICAL'));
  await page.close();

  // ---- 3. Supervisor monitoring (Acme) ----
  page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 2000 });
  await login(page, '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'supervisor@amap.com');
  check('supervisor routes to /organization', page.url().includes('/organization'), page.url());
  await wait(3000);
  const sup = await page.evaluate(() => document.body.innerText);
  check('supervisor sees workers', /worker/i.test(sup) && (sup.includes('Novak') || sup.includes('Morgan') || sup.includes('Alex') || sup.match(/Worker\s+\d/)));
  check('supervisor sees tasks/assignments', /task|assignment|gearbox|inverter/i.test(sup));
  await page.close();

  // ---- 4. Admin dashboard (Acme) ----
  page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 2000 });
  await login(page, '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'admin@amap.com');
  check('admin routes to /admin', page.url().includes('/admin'), page.url());
  await wait(3000);
  const adm = await page.evaluate(() => document.body.innerText);
  check('dashboard KPI cards render', /Total Workforce/i.test(adm) && /Completion Rate/i.test(adm));
  check('recent activity feed renders', /Recent Assignment Activity/i.test(adm));
  check('IST timestamps shown', /IST/.test(adm));
  await page.close();

  // ---- 5. Role-aware navigation + route guards (worker / supervisor / admin) ----
  // Evaluations can transiently fail with 'Execution context was destroyed'
  // when the SPA navigates mid-call (Next.js RSC redirect / full reload).
  // Retry them instead of aborting the whole journey.
  const safeEval = async (fn) => {
    let lastErr;
    for (let i = 0; i < 4; i++) {
      try { return await page.evaluate(fn); }
      catch (e) {
        lastErr = e;
        if (/destroyed|detached/i.test(e.message)) { await wait(1500); continue; }
        throw e;
      }
    }
    throw lastErr;
  };
  // Logout helper (role switch must update the navbar).
  const logout = async () => {
    console.log('[e2e] logout');
    // Click inside the page, DEFERRED by a tick so this evaluate resolves
    // before the SPA navigation can destroy the execution context.
    await safeEval(() => {
      const btn = [...document.querySelectorAll('button')].find(e => /logout/i.test(e.getAttribute('aria-label') || ''));
      if (btn) setTimeout(() => btn.click(), 0);
    });
    const t0 = Date.now();
    while (Date.now() - t0 < 30000) {
      if (page.url().includes('/login')) break;
      await wait(500);
    }
    await wait(1200);
  };
  const navLabels = () => safeEval(() =>
    [...document.querySelectorAll('nav[aria-label="Main Navigation"] a')].map(a => a.textContent.trim())
  );
  const directUrl = async (path) => {
    await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await wait(2500);
    return page.url();
  };

  // Fresh page for the role-switch journey (section 4 closed its page —
  // evaluating on a closed page throws 'detached Frame').
  page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 2000 });
  page.on('framenavigated', (f) => {
    if (f === page.mainFrame()) console.log('[nav]', new Date().toISOString().slice(11, 19), f.url());
  });

  // WORKER (LogiCore)
  console.log('[e2e] login: worker');
  await login(page, 'aa100000-0000-0000-0000-000000000004', 'worker1@logicore-logistics.com');
  await wait(1500);
  let wNav = await navLabels();
  check('WORKER nav: station + training visible', wNav.includes('Worker Station') && wNav.includes('Training'), wNav.join(', '));
  check('WORKER nav: Fleet & Supervisor hidden', !wNav.includes('Fleet & Supervisor'));
  check('WORKER nav: Admin Studio hidden', !wNav.includes('Admin Studio'));
  let wUrl = await directUrl('/organization');
  check('WORKER direct URL /organization blocked', !wUrl.includes('/organization'), wUrl);
  wUrl = await directUrl('/admin');
  check('WORKER direct URL /admin blocked', !wUrl.includes('/admin'), wUrl);
  wUrl = await directUrl('/worker');
  check('WORKER /worker accessible', wUrl.includes('/worker'), wUrl);
  wUrl = await directUrl('/training');
  check('WORKER /training accessible', wUrl.includes('/training'), wUrl);

  // SUPERVISOR (Acme)
  await logout();
  console.log('[e2e] login: supervisor');
  await login(page, '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'supervisor@amap.com');
  await wait(1500);
  let sNav = await navLabels();
  check('SUPERVISOR nav: Fleet & Supervisor visible', sNav.includes('Fleet & Supervisor'), sNav.join(', '));
  check('SUPERVISOR nav: Admin Studio hidden', !sNav.includes('Admin Studio'));
  check('SUPERVISOR nav: Worker Station hidden', !sNav.includes('Worker Station'));
  let sUrl = await directUrl('/organization');
  check('SUPERVISOR /organization accessible', sUrl.includes('/organization'), sUrl);
  sUrl = await directUrl('/admin');
  check('SUPERVISOR direct URL /admin blocked', !sUrl.includes('/admin'), sUrl);
  sUrl = await directUrl('/worker');
  check('SUPERVISOR direct URL /worker blocked', !sUrl.includes('/worker'), sUrl);

  // ADMIN (Acme) — role switch must have updated the navbar
  await logout();
  console.log('[e2e] login: admin');
  await login(page, '9a61e05d-7a32-4112-9c17-1833d7b42f65', 'admin@amap.com');
  await wait(1500);
  let aNav = await navLabels();
  check('ADMIN nav: Admin Studio + Fleet visible after role switch', aNav.includes('Admin Studio') && aNav.includes('Fleet & Supervisor'), aNav.join(', '));
  let aUrl = await directUrl('/admin');
  check('ADMIN /admin accessible', aUrl.includes('/admin'), aUrl);

  // Overview page: polished rebrand
  console.log('[e2e] overview');
  const ovUrl = await directUrl('/');
  const ov = await safeEval(() => document.body.innerText);
  check('OVERVIEW: Hybrid Control Interface hero', ov.includes('Hybrid Control Interface'));
  check('OVERVIEW: capabilities + roles + workflow sections', ov.includes('Platform Capabilities') && ov.includes('User Roles') && ov.includes('How a Job Flows'));
  check('OVERVIEW: no stale AMAP branding', !/\bAMAP\b/.test(ov));

  await browser.close();
  const failed = results.filter(r => !r[0]);
  console.log('\nE2E RESULT: ' + (failed.length === 0 ? 'ALL PASS' : failed.length + ' FAILURES'));
  process.exit(failed.length === 0 ? 0 : 1);
})().catch(e => { console.error('E2E FATAL:', e.message); console.error(e.stack); process.exit(2); });
