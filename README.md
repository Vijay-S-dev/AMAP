# Hybrid Control Interface (AMAP): Accessible Multimodal Assembly Platform

> **Enterprise-Grade Cyber-Physical Manufacturing Interface for Workers with Physical and Cognitive Diversities**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Backend Tests](https://img.shields.io/badge/tests-876%20passed-success)]()
[![Coverage](https://img.shields.io/badge/coverage-90.5%25-success)]()
[![WCAG](https://img.shields.io/badge/WCAG-2.1%20AA%20Compliant-blue)]()
[![Security](https://img.shields.io/badge/security%20audit-20%2F20%20passed-purple)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)]()
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)]()

---

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [API Reference](#api-reference)
- [AI Perception Layer](#ai-perception-layer)
- [Testing & CI](#testing--ci)
- [Security](#security)
- [Accessibility](#accessibility)
- [Project Status](#project-status)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## About the Project

Assembly-line software assumes a single, able-bodied interaction model:
precise mouse clicks, small touch targets, and steady hands. AMAP removes
that assumption. It is a hybrid control interface for manufacturing
execution systems that lets workers on the floor drive the same workflow
through **optical hand gestures**, **voice commands**, or traditional
input — chosen per worker, adapted to their body, and gated by the same
authorization model regardless of input channel.

The platform is built around one non-negotiable invariant. Every component
strictly enforces the fundamental architectural principle:

$$\mathbf{Recognition \neq Intent \neq Authorization \neq Execution}$$

- **Recognition:** Raw optical hand-tracking coordinates or acoustic speech transcription capture physical worker input.
- **Intent:** Multi-signal temporal fusion, fuzzy keyword normalization, and dwell accumulator establish confirmed semantic intent while filtering involuntary tremors.
- **Authorization:** Multi-tenant cryptographic JWT and role-based access control (RBAC) verify worker/supervisor/admin permissions and organization boundaries.
- **Execution:** Critical, irreversible manufacturing actions trigger mandatory secondary interlocks before sending control signals to physical machinery.

In other words: recognizing a fist never stops a machine by itself — it
only becomes a candidate intent, which must be authorized, confirmed, and
safety-gated before execution.

---

## Key Features

### Multimodal Interaction Engine
- **Optical Gesture Tracking:** Palm, Pinch, Thumbs Up, Point, Open Hand, and Fist recognition with temporal dwell smoothing (300ms–1500ms) to filter micro-tremors and involuntary spasms.
- **Acoustic Voice Pipeline:** On-device Vosk streaming speech-to-text (English + Hindi) with phonetic/fuzzy matching against a bounded vocabulary ("next step", "confirm", "pause", "emergency stop") and ambient noise thresholding — no audio ever leaves the machine.
- **Cross-Modal Fusion:** Reinforcing confidence booster ($c_f = 1 - (1 - c_1)(1 - c_2)$), complementary spatial binding (point at a target + say "confirm"), and safety confirmation gating on conflicting inputs.

### Evidence-Based Adaptation & Personalization
- **Rule of Evidence:** Never alters interaction parameters on single random outliers.
- **Pattern Evaluation:** Aggregates repeated difficulty signals (e.g. 4 low-confidence gesture events or dwell timeouts) to generate structured adaptation recommendations (e.g., increasing dwell time from 450ms to 600ms or enlarging touch targets).
- **Worker Gesture Mapping:** Personalized gesture-to-action overrides, resolved per worker with organization presets as fallback.

### Multi-Role Portals
- **Worker Workstation (`/worker`):** High-contrast HUD, step-by-step spatial target overlays, circular dwell timers, non-intrusive supervisor assistance calling, and physical emergency lockout.
- **Supervisor Station (`/organization`):** Real-time line telemetry, worker status monitoring, and instant assistance ticket escalation/resolution queue.
- **Admin Studio (`/admin`):** Factory floor preset tuning, adaptation review/approval panel, and tamper-proof audit trail exploration.

### AI Perception Layer
- **Unified multimodal pipeline** (`ai/` package): perception, intent recognition, and adaptation recommendations as a composable service, benchmarkable via `scripts/benchmark_ai.py`. See [`docs/AI.md`](docs/AI.md).

### Enterprise Security & Multi-Tenancy (20/20 Audit Passed)
- **PBKDF2 Hashing:** $\ge 600,000$ iterations with unique CSPRNG 32-byte salts.
- **Constant-Time Comparison:** All hashes, tokens, and signatures verified via `hmac.compare_digest`.
- **Row-Level Security (RLS):** Database-level tenant boundary isolation using PostgreSQL session contexts (`app.current_organization_id`).
- **Defensive Headers:** Strict CSP, nosniff, DENY framing, and Referrer policies.
- **Sliding-Window Rate Limiting:** Brute-force protection on authentication routes.

---

## Architecture

```text
AMAP/
├── backend/                  # FastAPI 0.115+ & Python 3.11+ Core Services
│   ├── app/                  # Application factory, CORS, and dependency injection
│   ├── middleware/           # Rate limiting, security headers, request IDs, logging
│   ├── models/               # Strict Pydantic v2 domain schemas (extra='forbid')
│   ├── repositories/         # 45 parameterized database repositories (SQL injection immune)
│   ├── routes/               # Modular REST endpoints (/auth, /sessions, /tasks, /multimodal, …)
│   ├── services/             # Pure domain business logic & multi-signal adaptation engines
│   ├── utils/                # PBKDF2 cryptography, Supabase RLS context, tenant scoping
│   └── tests/                # 876 automated tests (+24 Vosk model-gated STT tests that run in CI)
├── ai/                       # AI perception & intent pipeline (AIEngine / AIService)
├── frontend/                 # Next.js 14 / React 18 Accessible Workstation Studio
│   ├── app/                  # App Router (/worker, /organization, /admin, /)
│   ├── worker/               # Multimodal HUD, Workflow Viewer, Accessible Modals, Dwell Timers
│   ├── organization/         # Live Session Telemetry, Assistance Ticket Resolution Queue
│   ├── admin/                # Preset Config Studio, Adaptation Review, Immutable Audit Log
│   ├── shared/               # Vanilla CSS Design System Tokens (WCAG 2.1 AA, >=48px touch targets)
│   └── tests/                # Gesture engine, voice worklet, route-access unit tests
├── database/                 # PostgreSQL multi-tenant schema
│   ├── migrations/           # 53 structured SQL DDL migrations with Row-Level Security (RLS)
│   ├── schema/               # Canonical schema definitions
│   └── seed/                 # Seed datasets (applied by scripts/seed.py)
├── tests/                    # Platform-level e2e, integration, performance, security suites
├── scripts/                  # migrate.py, seed.py, setup_dev.py, run_all_tests.py, …
├── deployment/docker/        # Backend/frontend Dockerfiles, compose variants, nginx.conf
└── docs/                     # Technical specifications, architecture designs, API contracts
```

Deep dives: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (system design),
[`docs/AI.md`](docs/AI.md) (AI subsystem),
[`docs/VOICE_ARCHITECTURE.md`](docs/VOICE_ARCHITECTURE.md) (voice pipeline),
[`docs/DATABASE.md`](docs/DATABASE.md) (schema), and the full
[`docs/`](docs/README.md) documentation index.

---

## Quickstart

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 20+ |
| PostgreSQL | 16 (or Supabase local/cloud instance) |
| Docker (optional) | any recent version with Compose v2 |

### 1. Backend Setup

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Create and migrate the database (expects `DATABASE_URL`, see
[Configuration](#configuration)):

```bash
python ../scripts/migrate.py
python ../scripts/seed.py
```

Run the test suite and start the dev server:

```bash
python -m compileall app repositories routes middleware utils models services tests
pytest -q
```
*Expected output: `876 passed, 24 skipped in ~85s` (the 24 skips are real-STT tests that need prefetched Vosk models — CI always runs them; see [`docs/TESTING_AND_RELIABILITY.md`](docs/TESTING_AND_RELIABILITY.md)).*

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API docs are served at `http://127.0.0.1:8000/docs`.

> **Voice STT (optional locally):** the streaming voice tests and pipeline
> need local Vosk models (~1 GB): `python scripts/prefetch_vosk_models.py`.

### 2. Frontend Setup

```bash
cd frontend
npm install          # also generates the MediaPipe gesture assets
npm run dev
```

Open `http://localhost:3000` to launch the Hybrid Control Interface Multimodal Suite.

### One-command alternative

`python scripts/setup_dev.py` from the repository root bootstraps the
development environment end to end.

---

## Usage

### Demo login (seeded data)

The seed script provisions demo accounts for each role. Worker login:

| Field | Value |
|---|---|
| Organization ID | `9a61e05d-7a32-4112-9c17-1833d7b42f65` |
| Email | `alex.worker@amap.com` |
| Password | `SecurePassword123!` |

Open `http://localhost:3000`, sign in, and try the three portals:
`/worker` (multimodal HUD with dwell timers), `/organization`
(supervisor telemetry and assistance queue), and `/admin` (presets,
adaptation review, audit log).

### Try the API from the terminal

These are the exact requests CI verifies on every push — copy-paste ready
against a running stack:

```bash
# 1. Health check
curl -fsS http://localhost:8000/api/v1/health

# 2. Log in as the demo worker
TOKEN=$(curl -fsS -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"organization_id":"9a61e05d-7a32-4112-9c17-1833d7b42f65","email":"alex.worker@amap.com","password":"SecurePassword123!"}' \
  | python -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# 3. Fuse a thumbs-up gesture into an action intent
curl -fsS -X POST http://localhost:8000/api/v1/multimodal/fuse \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"inputs":[{"mode":"gesture","raw_intent":"thumbs_up","confidence":0.92,"timestamp_ms":1700000000000}],"temporal_window_ms":1500}'
# -> {"fused_action":"confirm_action", "validation_status":"valid", …}

# 4. Execute the confirmed action (audited + safety-gated)
curl -fsS -X POST http://localhost:8000/api/v1/actions/execute \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"action_name":"confirm_action","parameters":{"source":"readme-demo"}}'
# -> {"success": true, …}
```

---

## Configuration

Copy [`.env.example`](.env.example) to `.env` and adjust. The application
never requires secrets for local development — production mode enforces
them at startup.

### Application

| Variable | Default | Notes |
|---|---|---|
| `ENVIRONMENT` | `development` | `production` enables strict secret/CORS validation |
| `APP_NAME` | `AMAP Backend` | |
| `API_VERSION_PREFIX` | `/api/v1` | |
| `LOG_LEVEL` | `INFO` | |
| `ENABLE_DEV_DEMO_USERS` | `false` | Demo-account fallback; must be `false` in production |

### Database & authentication

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | — | **Required.** e.g. `postgresql://amap_user:…@localhost:5432/amap` |
| `JWT_SECRET_KEY` | dev value | **Required in production**, min 32 chars, secure random |
| `JWT_ALGORITHM` | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | |
| `CORS_ALLOWED_ORIGINS` | dev default | **Required in production**, comma-separated origins |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` | empty | Optional Supabase integration |

### Docker Compose

| Variable | Default | Notes |
|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `amap_user` / `amap_password` / `amap` | Database container credentials |
| `POSTGRES_PORT` | `5432` | Host port for PostgreSQL |
| `BACKEND_PORT` | `8000` | Host port for the API |
| `FRONTEND_PORT` | `3000` | Host port for the web app |
| `AMAP_ENV` | `development` | Backend `ENVIRONMENT` inside compose |
| `VOSK_TIER` | `large` | Build-time Vosk model tier: `large` \| `small` \| `lgraph` \| `indian` \| `indian-large` |

> **Memory-constrained hosts:** the `large` English model needs roughly
> 1.5 GB RAM per backend process. Build with `VOSK_TIER=indian` (or
> `lgraph`) to run comfortably on 8 GB machines.

---

## Docker Deployment

The full stack — PostgreSQL 16, migrations + seed, FastAPI backend with the
Vosk voice pipeline, and the Next.js frontend — runs from a clean checkout:

```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/health    # {"status":"ok"}
```

| Service | Image | Port | Notes |
|---|---|---|---|
| `postgres` | `postgres:16` | 5432 | Health-checked; data in `amap_postgres_data` volume |
| `migrate` | `amap-backend:local` | — | One-shot: applies all 53 migrations, then seeds |
| `backend` | `amap-backend:local` | 8000 | FastAPI + baked-in Vosk models (`VOSK_TIER` build arg) |
| `frontend` | built from `deployment/docker/Dockerfile.frontend` | 3000 | Next.js standalone server |

Environment-specific variants (`deployment/docker/docker-compose.dev.yml`,
`docker-compose.prod.yml`) and the reverse-proxy config
(`deployment/docker/nginx.conf`) live in [`deployment/docker/`](deployment/docker/).

> **Docker Hub descriptions.** No images are published to a registry yet —
> everything builds locally. Ready-to-paste Docker Hub descriptions are
> staged in [`deployment/docker/description/`](deployment/docker/description/)
> (short description validated at ≤100 characters by
> `python scripts/validate_docker_description.py`, which also runs in CI).

---

## API Reference

Interactive documentation is generated from the code:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Contract document:** [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md)

Main endpoint groups under `/api/v1`:

| Group | Module | Purpose |
|---|---|---|
| `/auth` | `routes/auth.py` | Login, tokens, demo users (rate-limited) |
| `/sessions` | `routes/sessions.py` | Work-session lifecycle + heartbeats |
| `/tasks` | `routes/tasks.py` | Task and workflow assignments |
| `/gestures` | `routes/gestures.py` | Optical hand-frame processing |
| `/voice` | `routes/voice.py` | Streaming speech-to-text WebSocket |
| `/multimodal` | `routes/multimodal.py` | Cross-modal intent fusion |
| `/actions` | `routes/actions.py` | Safety-gated action execution |
| `/interactions` | `routes/interactions.py` | Interaction event telemetry |
| `/personalization` | `routes/personalization.py` | Worker adaptation profiles + gesture maps |
| `/assistance` | `routes/assistance.py` | Assistance requests + notifications |
| `/supervisor`, `/organization_management` | `routes/supervisor.py` | Line telemetry, escalation, management |
| `/admin`, `/permissions` | `routes/admin.py` | Presets, adaptation review, audit, RBAC |
| `/accessibility`, `/readiness`, `/health`, `/database` | | Accessibility prefs, readiness/health probes, DB checks |

All endpoints require org-scoped JWT auth except health/readiness. Errors
use a consistent `{"error": "…"}` envelope.

---

## AI Perception Layer

The `ai/` package implements the perception/intent/adaptation layer as a
unified pipeline (`MultimodalAIPipeline`, `AIService`) with its own
hyperparameter configuration (`ai/config.py`) and CLI (`ai/cli.py`). It is
covered by [`docs/AI.md`](docs/AI.md) and can be benchmarked end to end:

```bash
python scripts/benchmark_ai.py
```

The layer obeys the same invariant as the rest of the platform: it
produces **intent candidates and adaptation recommendations** — it never
authorizes or executes anything itself.

---

## Testing & CI

Every push and pull request runs the full quality gate in
[`.github/workflows/ci.yml`](.github/workflows/ci.yml):

1. Migrations + seed on a fresh PostgreSQL 16
2. Complete backend suite with prefetched Vosk models (real-STT tests must
   not skip) and a **coverage gate of 85%** (measured baseline: 90.5%)
3. Platform suites (`tests/e2e`, `tests/integration`, `tests/security`)
4. Critical E2E over real HTTP with PostgreSQL assertions
5. Frontend typecheck, lint, 142 unit tests, and production build
6. `docker compose` build + up + readiness + login/fusion/execute smoke

Locally: `pytest -q` in `backend/`, `npm run test:engine` in `frontend/`,
or everything at once via `python scripts/run_all_tests.py`. Full details —
test pyramid, coverage policy, and the skipped-test analysis — live in
[`docs/TESTING_AND_RELIABILITY.md`](docs/TESTING_AND_RELIABILITY.md). Optional pre-commit hooks are defined
in [`.pre-commit-config.yaml`](.pre-commit-config.yaml)
(`pip install pre-commit && pre-commit install`).

---

## Security

All 20 mission-critical security criteria are covered with automated tests in `backend/tests/test_security_audit_all_20.py`:

- [x] **01. PBKDF2 Iterations & Salts:** 600k iterations, 32-byte CSPRNG salt
- [x] **02. Constant-Time Verification:** `compare_digest` prevents timing side-channels
- [x] **03. JWT Signature Integrity:** HS256 algorithm enforcement, reject forged tokens
- [x] **04. Expiration Lifecycle:** Strict token expiry checks returning 401 Unauthorized
- [x] **05. Production Secrets Guard:** Block dev secrets when `ENVIRONMENT=production`
- [x] **06. SQL Injection Immunity:** 100% parameterized queries across all repositories
- [x] **07. Organization Multi-Tenant Isolation:** Zero cross-tenant data leakage
- [x] **08. Worker Self-Data Scoping:** Worker cannot access peer personalization profiles
- [x] **09. RBAC Permission Gating:** Granular route dependencies on all admin endpoints
- [x] **10. Invariant Separation:** Recognition != Intent != Authorization != Execution
- [x] **11. Safety Interlocks:** Mandatory confirmation dialogues on critical commands
- [x] **12. CORS Origin Whitelisting:** Strict origin validation in production
- [x] **13. Defensive Security Headers:** CSP, X-Frame-Options, nosniff, Referrer-Policy
- [x] **14. Pydantic Sanitization:** `extra = 'forbid'` prevents payload property injection
- [x] **15. Credential Masking:** Passwords and tokens excluded from application logs
- [x] **16. Rate Limiting:** Sliding-window throttle on `/auth/login` returning 429
- [x] **17. Immutable Audit Logs:** DELETE and UPDATE operations strictly prohibited
- [x] **18. Centralized Exception Shielding:** Internal tracebacks hidden in production
- [x] **19. Supabase Row-Level Security:** Database-level policy enforcement
- [x] **20. Temporal Dwell Safety:** Tremor smoothing and continuous hold thresholds

Reporting a vulnerability: see [`SECURITY.md`](SECURITY.md) — practices
and policy details in [`docs/SECURITY_AND_PRIVACY.md`](docs/SECURITY_AND_PRIVACY.md).

---

## Accessibility

Compliance is verified by automated tests, not claimed by checklist:

| Standard | Hybrid Control Interface Implementation | Verified By |
|---|---|---|
| **Touch Target Size** (2.5.5 / 2.5.8) | `min-height: 48px`, `min-width: 48px` on all interactive elements | `test_wcag_css_design_system_tokens_and_accessibility` |
| **Focus Visible** (2.4.7) | High-visibility `:focus-visible` outline rings with 3px offset | `test_wcag_css_design_system_tokens_and_accessibility` |
| **Contrast Ratios** (1.4.3 / 1.4.6) | High-contrast mode switch providing pure `#000000` background and `#ffffff` text | `test_wcag_css_design_system_tokens_and_accessibility` |
| **Screen Reader Feedback** (4.1.3) | `aria-live="polite"` on HUD updates; `role="alert"` on Emergency Stop | `test_wcag_screen_reader_live_regions_in_worker_station` |
| **Non-Color Reliance** (1.4.1) | Dual-channel state representation (Icon + Text + Badge) | `test_wcag_non_reliance_on_color_alone` |
| **Dialog Semantics** (2.1) | Accessible modals with `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` | `test_wcag_accessible_modal_dialog_semantics` |

---

## Project Status

**Active development.** AMAP originates from an HCI research context
(accessible manufacturing interfaces) and is evolving toward a deployable
platform. All merges are CI-gated (tests, coverage, E2E, compose smoke);
no releases have been tagged yet. Expect schema and API changes until the
first tagged version — see [Roadmap](#roadmap).

---

## Roadmap

Priorities and reasoning are maintained in [`docs/ROADMAP.md`](docs/ROADMAP.md). Highlights:

- Push supervisor-service test coverage (currently 72%) up to the suite average
- Versioning policy and tagged releases (enables live CI/version badges)
- Publish images to a container registry and sync the staged Docker Hub descriptions
- Real screenshots and a demo GIF for this README (none exist yet)
- Performance suite in CI (today it is local-only due to shared-runner timing noise)
- Voice support beyond English and Hindi

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full guide. In brief:

1. Fork or branch from `main`; keep changes focused.
2. Install the optional hooks: `pip install pre-commit && pre-commit install`.
3. Run the gates before opening a PR — at minimum
   `pytest -q` (backend), `npm run typecheck && npm run lint && npm run test:engine` (frontend).
4. Open a pull request; CI must be fully green before merge
   (tests + 85% coverage floor + E2E + compose smoke).

Architecture decisions are recorded in [`docs/DECISIONS.md`](docs/DECISIONS.md);
please propose significant changes there first. Notable changes are logged
in [`CHANGELOG.md`](CHANGELOG.md).

---

## Support

- **Bugs and feature requests:** [GitHub Issues](https://github.com/Vijay-S-dev/AMAP/issues)
- **Architecture & design questions:** [`docs/`](docs/README.md) index first, then open an issue labeled `question`

---

## License

This project is licensed under the MIT License — see [`LICENSE`](LICENSE).
