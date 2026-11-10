# Testing Guide

How to run every test suite in this repository, the coverage policy, and
the analysis of every skipped test.

**Current baseline (2026-09, post org-refactor):** 876 backend tests passed
+ 24 model-gated skips (run in CI), 90.5% total coverage, ~83 s wall clock;
frontend 142 unit tests (gesture engine 58, voice worklet 28, route-access
56); platform suites 6 tests — all green in CI.

---

## Test pyramid

AMAP follows a unit-first pyramid — cheap, fast, deterministic tests at the
bottom; few expensive full-stack tests at the top:

| Layer | Where | Count | Runtime | Runs in CI |
|---|---|---|---|---|
| Unit (services, models, repositories, routes, config) | `backend/tests/test_*.py` | ~850 | seconds | yes |
| Voice/STT with real Vosk models | `backend/tests/test_vosk_*.py`, `test_phase11_voice_e2e.py` | 24 | ~20 s | yes (models prefetched) |
| Frontend unit (engine logic, policy) | `frontend/src/**/*.test.ts` | 142 | ~10 s | yes |
| Platform integration (in-process TestClient) | `tests/e2e`, `tests/integration`, `tests/security` | 6 | ~2 s | yes |
| Critical E2E over real HTTP | `scripts/ci_e2e.py` | 1 flow | ~30 s | yes |
| Compose smoke (real containers) | CI `docker` job | 1 flow | ~3 min | yes |
| Performance / timing | `tests/performance` | — | minutes | no (timing-sensitive; run locally via `scripts/run_all_tests.py`) |

## Backend (Python / FastAPI)

Requires a reachable, migrated + seeded PostgreSQL (see `docker-compose.yml`
or `.env.example`) and `DATABASE_URL` set.

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
pytest -q
```

Expected on a machine **without** prefetched Vosk models:
`876 passed, 24 skipped` (~83 s). The 24 skips are real-STT tests that
require the local Vosk models — see "Skipped-test analysis" below. CI
prefetches the models, so the same suite reports **900 passed, 0 skipped**
there; any local skip that is *not* model-gated is a bug.

### Coverage

Coverage is a **diagnostic, not a target**: it tells you where risk lives,
it does not prove correctness. To keep it honest:

- **Policy floor: 80%.** New modules should not land under this.
- **CI gate: 85%** (`--cov-fail-under=85` in `.github/workflows/ci.yml`) —
  a ratchet with 5 points of headroom over the floor so normal variance
  (e.g. model-gated paths) never fails a build spuriously.
- **Measured baseline: 90.5%** (7,202 statements / 684 missed).

Run locally with the same flags CI uses:

```bash
cd backend
pytest -q \
  --cov=app --cov=middleware --cov=models --cov=repositories \
  --cov=routes --cov=services --cov=utils \
  --cov-report=term-missing --cov-fail-under=85
```

Known low-coverage modules and why (all reviewed, none alarming):

| Module | Coverage | Reason |
|---|---|---|
| `services/supervisor_service.py` | 72% | Largest service (441 stmts). The uncovered blocks are multi-repository operational flows — task reassignment (686–744), escalation, and the report/export generators (865–942) — each needing five mocked repositories in sequence. Documented follow-up; the exported routes' happy paths are covered. |
| `routes/supervisor.py` | 76% | Error-mapping branches of the supervisor endpoints (404/403/400 translations); happy paths covered. |
| `services/vosk_stt_service.py` | 65% | Model-gated: the uncovered lines are the real-model load/decode paths that only execute when Vosk models are provisioned (covered in CI). |

`routes/sessions.py` and `services/assistance_service.py` were the previous
low spots (59% / 68%); dedicated contract tests
(`tests/test_sessions_routes_http.py` — heartbeat branches + every
exception→status mapping, and `tests/test_assistance_service.py` —
ownership guards + field pass-through) brought both to **100%**.

---

## Skipped-test analysis

Full inventory as of the baseline above. **Every skip is
environment-dependent and documented; none are obsolete, flaky, or
commented-out tests.** All 24 share one root cause:

> The machine running the suite has not provisioned the local Vosk speech
> models (`python scripts/prefetch_vosk_models.py` — downloads ~1 GB into
> `backend/.vosk_cache/`). The tests that need real audio decoding guard on
> `MODELS_PRESENT` and skip with a reason string that names the prefetch
> script, so no skip is ever undocumented.

| File | Tests skipped | Guard | What they verify |
|---|---|---|---|
| `tests/test_vosk_streaming.py` | 18 | module-level `MODELS_PRESENT` | Real streaming transcription over the WebSocket voice pipeline (partial results, finalization, multi-utterance). |
| `tests/test_phase11_voice_e2e.py` | 4 | `MODELS_PRESENT` per test | Voice E2E: mic-socket → STT → intent match → action dispatch with real audio buffers. |
| `tests/test_vosk_stt_service.py` | 2 | `MODELS_PRESENT` per test | Vosk service model load + transcribe against the bundled sample WAV. |

Remediation status: **none required.**

- In CI the models are prefetched and cached
  (`actions/cache` on `backend/.vosk_cache`), so these tests *always run
  there* — a regression in the real STT path cannot merge silently.
- Locally, running them is opt-in (`python scripts/prefetch_vosk_models.py`
  then `pytest tests/test_vosk_streaming.py -q`), which is the right
  trade-off for developer machines with limited disk/RAM.
- A sixth historical skip site (`tests/test_phase6_workflows.py`,
  "seed workflow not present") does **not** skip against a properly seeded
  database — it is a data guard, not a test gap.

If you ever see skips beyond these 24 (or skips whose reason does not name
an environment precondition), treat it as a test bug and fix or remove the
test.

---

## Platform-level suites (root `tests/`)

Cross-cutting suites that exercise the assembled platform through the
in-process FastAPI `TestClient` against a migrated + seeded database:

```bash
# from the repo root, with DATABASE_URL pointing at the seeded DB
python -m pytest tests/e2e tests/integration tests/security -q
```

These run in CI as a dedicated step after the backend suite.
`tests/performance` is timing-sensitive and deliberately excluded from CI
(shared runners give noisy timings); run it locally via the full runner:

```bash
python scripts/run_all_tests.py
```

which executes every backend suite plus the root `tests/` suites and the
frontend engine tests, and prints one summary table.

## Frontend (Next.js / TypeScript)

```bash
cd frontend
npm ci
npm run typecheck        # tsc --noEmit
npm run lint             # eslint
npm run test:engine      # gesture engine + voice worklet + route-access unit tests
npm run build            # production build
```

## CI (GitHub Actions)

`.github/workflows/ci.yml` runs, on every push/PR:

1. Migrations + seed against a real PostgreSQL
2. Backend test suite with prefetched Vosk models (real STT tests must not
   skip) **and a coverage gate of 85%**
3. Platform suites (`tests/e2e`, `tests/integration`, `tests/security`)
4. Critical E2E over real HTTP + PostgreSQL
5. Frontend typecheck, lint, unit tests, and production build
6. `docker compose` build + up + readiness + login/fusion/execute smoke

## Pre-commit hooks (optional, recommended)

`.pre-commit-config.yaml` defines fast staged-file checks (whitespace
hygiene, YAML/TOML validity, merge-conflict markers, large-file guard, and
a Python syntax gate via `compileall`). Install once per clone:

```bash
pip install pre-commit
pre-commit install          # hooks now run on every git commit
pre-commit run --all-files  # after applying a patch, to re-check everything
```

## Docker smoke check

```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/health   # {"status":"ok"}
```
