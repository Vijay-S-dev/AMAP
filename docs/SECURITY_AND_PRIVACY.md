# Security & Privacy Practices

This document describes the security and privacy practices implemented in
the AMAP codebase. It reflects what is actually implemented and tested — it
is not a certification or an external audit report.

## Authentication

- **Password hashing:** PBKDF2-SHA256 with ≥600,000 iterations and a unique
  CSPRNG-generated 32-byte salt per password (`backend/utils/`).
- **Constant-time comparison:** all secret comparisons (password hashes,
  tokens, signatures) use `hmac.compare_digest` — never `==`.
- **JWT sessions:** HS256-signed access tokens carrying the user id,
  organization id, roles, permissions, and worker profile id
  (`backend/services/auth_service.py`).
- **Secrets via environment:** `JWT_SECRET_KEY`, `DATABASE_URL`, and friends
  are read from the environment (see `.env.example`); no secrets are
  committed. Production mode refuses to start with a default/short JWT key.

## Authorization (multi-tenant)

- **RBAC:** role + permission model (worker / supervisor / admin) enforced on
  every route via FastAPI dependencies.
- **Row-Level Security:** PostgreSQL RLS isolates organizations at the
  database level using the session context variable
  `app.current_organization_id` (migration
  `database/migrations/040_supabase_row_level_security.sql`).
- **Tenant scoping:** all repositories filter by organization; parameterized
  SQL everywhere (no string-concatenated queries).

## Hardening

- **Security headers:** strict CSP, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, and Referrer-Policy set by middleware.
- **Rate limiting:** sliding-window brute-force protection on the
  authentication routes (`backend/middleware/rate_limiting.py`).
- **CORS:** environment-driven allowlist; never unrestricted in production
  (enforced at startup, `backend/app/config.py`).
- **Audit trail:** tamper-evident audit events for administrative and
  security-relevant actions.

## Privacy & data handling

AMAP processes biometric-adjacent data — camera frames of hands and
microphone audio — plus worker-profile data. The governing rules:

- **On-device processing only.** Hand landmarks are computed in the browser
  (MediaPipe WASM) and speech-to-text runs on the backend with local Vosk
  models. No camera frames, audio, or transcripts are sent to any external
  service, and none persist beyond the recognition step.
- **No raw-signal storage.** The database stores derived events (recognized
  gesture name, fused intent, action, audit records) — not raw video or
  audio.
- **Worker-profile data is tenant-scoped.** Personalization profiles and
  adaptation data live inside the organization boundary enforced by RLS;
  workers cannot read peers' profiles (security-audit criterion 08).
- **Audit retention.** Audit events are append-only (`REVOKE UPDATE,
  DELETE`) and retained for accountability; access to them is admin-gated.
- **Demo credentials.** Seeded accounts use deterministic development-only
  passwords (`SecurePassword123!`) and are disabled unless
  `ENABLE_DEV_DEMO_USERS` is set; the flag is forced off in production.
- **Logs.** Passwords, tokens, and secrets are masked in application logs
  (security-audit criterion 15).

## AI safety

The AI perception layer (`ai/`) and the adaptation engine obey the platform
invariant **Recognition ≠ Intent ≠ Authorization ≠ Execution**:

- AI components produce **intent candidates and adaptation recommendations
  only** — they never authorize or execute actions.
- Safety-critical actions always require a human secondary confirmation
  (interlock), regardless of recognition confidence.
- The evidence-based adaptation rule guarantees no interaction parameter
  changes on single outliers — only repeated, aggregated difficulty signals.
- AI processing is deterministic over its inputs (no external model calls),
  so behavior is reproducible and testable.

## Reporting

Suspected vulnerabilities should be reported privately to the repository
maintainers. Please do not open public issues for security reports. The
root [`SECURITY.md`](../SECURITY.md) describes the reporting path.
