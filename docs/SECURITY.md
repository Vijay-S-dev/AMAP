# Security Practices

This document describes the security practices implemented in the AMAP
codebase. It reflects what is actually implemented and tested — it is not a
certification or an external audit report.

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

## Reporting

Suspected vulnerabilities should be reported privately to the repository
maintainers. Please do not open public issues for security reports.
