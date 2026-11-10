# Security Policy

## Reporting a vulnerability

We take security issues seriously and appreciate responsible disclosure.

**Please report suspected vulnerabilities privately to the repository
maintainers — do not open public issues for security reports.**

- Open a [GitHub security advisory](https://github.com/Vijay-S-dev/AMAP/security/advisories/new)
  for this repository, or
- contact the maintainers directly through a private channel (repository
  owner: [@Vijay-S-dev](https://github.com/Vijay-S-dev)).

Include what you found, how to reproduce it, and any impact assessment.
You will hear back within a few days. Please avoid public disclosure until
a fix is released.

## Scope

Everything in this repository is in scope: the FastAPI backend, the
Next.js frontend, database migrations, Docker/deployment configuration,
and CI workflows.

## Security model in brief

AMAP is a multi-tenant manufacturing platform enforcing
**Recognition ≠ Intent ≠ Authorization ≠ Execution**:

- PBKDF2-SHA256 (≥600k iterations, unique CSPRNG salts) password hashing;
  constant-time comparisons everywhere.
- HS256 JWT sessions; production mode refuses weak/default secrets at
  startup.
- PostgreSQL row-level security isolates organizations; parameterized SQL
  only.
- Rate-limited authentication; strict security headers; append-only audit
  trail.
- On-device processing of camera and microphone data — no biometric data
  leaves the machine.

The 20 security-audit criteria are enforced by automated tests
(`backend/tests/test_security_audit_all_20.py`) and must remain passing
for any change to merge.

Detailed practices: [`docs/SECURITY_AND_PRIVACY.md`](docs/SECURITY_AND_PRIVACY.md).
