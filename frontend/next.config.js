const { execSync } = require('child_process');

/**
 * Human-readable build stamp (git short hash + UTC build time), inlined
 * into the client bundle at build time. Rendered in the overview footer
 * so anyone can instantly verify WHICH build the browser is showing.
 * Falls back to 'unknown' where git isn't available (e.g. Docker builds).
 */
function buildStamp() {
  try {
    const hash = execSync('git rev-parse --short HEAD', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    const built = new Date().toISOString().replace('T', ' ').slice(0, 16);
    return `${hash} • ${built} UTC`;
  } catch {
    return 'unknown';
  }
}

/** @type {import('next').NextConfig} */

// Backend origin for the same-origin API proxy below. In Docker/production the
// frontend typically sets NEXT_PUBLIC_API_BASE_URL to the backend directly and
// this rewrite is simply unused; for local dev and hosted previews it lets the
// browser call a relative /api/v1/* (no CORS, no localhost-from-browser issue).
const backendOrigin = process.env.BACKEND_ORIGIN || 'http://127.0.0.1:8000';

const nextConfig = {
  reactStrictMode: true,
  env: { NEXT_PUBLIC_BUILD_INFO: buildStamp() },
  // Required by deployment/docker/Dockerfile.frontend (standalone server bundle).
  output: 'standalone',
  // Cache policy: HTML and API responses must NEVER be served from a cache
  // (a stale HTML page = users seeing an old UI after a redeploy — exactly
  // the failure this fixes). Content-hashed /_next/static assets are the
  // exception: they are immutable per build and stay long-cacheable.
  async headers() {
    return [
      { source: '/:path*', headers: [{ key: 'Cache-Control', value: 'no-store' }] },
      { source: '/_next/static/:path*', headers: [{ key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }] },
      { source: '/api/:path*', headers: [{ key: 'Cache-Control', value: 'no-store' }] },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendOrigin}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
