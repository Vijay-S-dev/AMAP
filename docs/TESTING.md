# Testing Guide

How to run every test suite in this repository.

## Backend (Python / FastAPI)

Requires a reachable PostgreSQL (see `docker-compose.yml` or `.env.example`)
and `DATABASE_URL` set.

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
pytest -q
```

The suite covers unit, integration, and security tests for services,
repositories, routes, and the Vosk streaming voice pipeline (800+ tests;
real-STT tests need the Vosk models prefetched — skipped otherwise).

## Frontend (Next.js / TypeScript)

```bash
cd frontend
npm ci
npm run typecheck        # tsc --noEmit
npm run lint             # eslint
npm run test:engine      # gesture engine + voice worklet + route-access unit tests
npm run build            # production build
```

## Platform-level suites (root `tests/`)

Cross-cutting suites that exercise the whole platform over real HTTP:

```bash
python scripts/run_all_tests.py
```

Runs `tests/e2e/`, `tests/integration/`, `tests/performance/`, and
`tests/security/` (manual runner — not currently part of CI; see
`docs/DECISIONS.md`).

## CI (GitHub Actions)

`.github/workflows/ci.yml` runs, on every push/PR:

1. Migrations + seed against a real PostgreSQL
2. Backend test suite (with prefetched Vosk models — real STT tests must not skip)
3. Critical E2E over real HTTP + PostgreSQL
4. Frontend typecheck, lint, unit tests, and production build

## Docker smoke check

```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/health   # {"status":"ok"}
```
