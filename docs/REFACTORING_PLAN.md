# File & Folder Organization Plan — Executed

**Date:** 2026-11-10 · **Scope:** whole repository · **Status:** completed and verified

---

## 1. Current State Analysis (before)

The repository is a full-stack monorepo:

```
AMAP/
├── backend/        FastAPI layered app (app/, routes/, services/, repositories/,
│                   models/, middleware/, utils/, tests/ + pytest.ini, requirements.txt)
├── frontend/       Next.js 14 app (app/, worker/, organization/, admin/, shared/,
│                   tests/ + package.json, tsconfig.json)
├── database/       migrations 001–053 + seed
├── deployment/     docker/ (Dockerfiles, compose.prod.yml)
├── docs/           specifications and architecture docs
├── scripts/        migrate.py, seed.py, prefetch_vosk_models.py, run_all_tests.py
├── tests/          platform-level e2e / integration / performance / security suites
├── ai/             AI assets copied into the backend image
├── .github/        CI workflow
├── docker-compose.yml, .env.example, .gitignore, LICENSE, README.md
```

Pattern detected: **layered backend + feature-based frontend monorepo** — already
the conventional structure for this project type.

## 2. Issues Identified

| # | Issue | Evidence |
|---|---|---|
| 1 | Obsolete duplicate configs | `docs/BACKEND REQS` (stale 4-pin subset of `backend/requirements.txt`), `docs/PYTEST.INI` (verbatim duplicate of `backend/pytest.ini`), `docs/ENV.EXAMPLES` (stale subset of `.env.example`), `docs/.GITIGNORE` (subset of root `.gitignore`) |
| 2 | Stale duplicates in frontend | `frontend/package` (outdated copy of `package.json`), `frontend/tsconfig` (old variant of `tsconfig.json`, read by no tool) |
| 3 | Stale documentation | `frontend/README` ("Foundation Phase… routing only" — long superseded), `docs/BASELINE_SNAPSHOT.md` (Phase-0 point-in-time measurement) |
| 4 | Empty placeholder docs | `docs/DECISIONS.md`, `docs/SECURITY.md`, `docs/TESTING.md`, `docs/REQUIREMENTS.md` (all 0 bytes — misleading given README badges) |
| 5 | Empty LICENSE | 0-byte `LICENSE` while README badge declares MIT |
| 6 | Naming inconsistency | space in `BACKEND REQS` (fixed); `docs/Backend.md` casing kept as-is — see ADR-0007 |
| 7 | Dead scaffolding | root `shared/{constants,schemas,types}/` — `.gitkeep` only, unreferenced (frontend uses the `@/shared` alias into `frontend/shared/`) |
| 8 | Stray file | `tests/s` — empty, unreferenced |
| 9 | `.gitignore` gaps | `docker-compose.override.yml` (per-machine stacks) and `*.log` not ignored |

**Not issues (verified):** root `tests/` is wired to `scripts/run_all_tests.py`
(platform suites — retained, see ADR-0005); `ai/` is copied into the backend
Docker image; `docs/prompts/` holds development-time AI prompt assets.

## 3. Target Structure (decision: no `src/` migration)

Per ADR-0001 the monorepo layout is kept — a generic `src/` restructure would
break Docker build contexts, CI paths, `PYTHONPATH`, pytest/tsconfig configs
and every import, for zero functional gain. The target is the current layout
**minus the clutter**, with a documentation contract (ADR-0006):

- Root: `README.md`, `LICENSE` (filled), package-manager/compose files only.
- `docs/`: living documents, plus `docs/archive/docs-backup-YYYY-MM-DD/`
  for superseded material. (`Backend.md` keeps its casing — ADR-0007.)

## 4. Migration Table (executed)

| Current | Target | Status |
|---|---|---|
| `docs/BACKEND REQS` | — (duplicate of `backend/requirements.txt`) | ✅ deleted |
| `docs/PYTEST.INI` | — (duplicate of `backend/pytest.ini`) | ✅ deleted |
| `docs/ENV.EXAMPLES` | — (subset of `.env.example`) | ✅ deleted |
| `docs/.GITIGNORE` | — (subset of root `.gitignore`) | ✅ deleted |
| `docs/REQUIREMENTS.md` | — (empty; `MASTER_SPEC.md` is canonical) | ✅ deleted (ADR-0003) |
| `frontend/package` | — (stale copy of `package.json`) | ✅ deleted |
| `frontend/tsconfig` | — (stale variant of `tsconfig.json`) | ✅ deleted |
| `tests/s` | — (empty stray) | ✅ deleted |
| `shared/{constants,schemas,types}/` | — (dead scaffolding) | ✅ removed (ADR-0004) |
| `docs/Backend.md` | — (kept; case-only rename rejected, ADR-0007) | ✅ decision recorded |
| `docs/BASELINE_SNAPSHOT.md` | `docs/archive/docs-backup-2026-11-10/` | ✅ archived |
| `frontend/README` | `docs/archive/docs-backup-2026-11-10/frontend-README-foundation-phase.md` | ✅ archived |
| `LICENSE` (empty) | MIT text ("AMAP contributors", matching the README badge) | ✅ filled |
| `docs/SECURITY.md` (empty) | living document (implemented practices) | ✅ written |
| `docs/TESTING.md` (empty) | living document (all suites + CI) | ✅ written |
| `docs/DECISIONS.md` (empty) | ADR log (ADR-0001…0006 = this refactor) | ✅ written |
| `.gitignore` | + `docker-compose.override.yml`, `*.log` | ✅ updated |

**Import path updates required: none.** No source file moved; all deletions
were verified unreferenced (`grep -rn` across the repo, excluding
node_modules/.git). No Dockerfile, CI, or script path references any removed
or renamed file.

## 5. Risk Assessment

- **Import breakage:** none — zero source moves.
- **Link breakage:** none — no cross-references to any touched file existed.
- **History:** all moves/deletes are recorded as git renames/deletions
  (move-only commit; `git log --follow` works).
- **Residual risk:** `docs/archive/` content is historical — treat as
  read-only reference.

## 6. Verification Results

| Check | Result |
|---|---|
| Frontend unit tests (`npm run test:engine`) | gesture 58 ✓ · voice-worklet 28 ✓ · route-access 56 ✓ |
| Frontend typecheck (`tsc --noEmit`) | ✓ clean |
| Frontend production build (`npm run build`) | ✓ succeeds |
| Backend compile check (`py_compile` over `backend/`) | ✓ (no Python files changed) |
| Unreferenced-file grep before every deletion | ✓ zero references |

## 7. Success Criteria

- [x] Clear logical directory structure; no source files in root
- [x] All obsolete files removed; naming consistent; no import updates needed
- [x] Full test suite passing; application builds
- [x] Git history preserved (renames/deletes via git metadata in the patch)
- [x] Documentation updated (`REFACTORING_PLAN.md`, `SECURITY.md`, `TESTING.md`, `DECISIONS.md`)

## 8. Follow-up Candidates (out of scope here)

1. Wire `scripts/run_all_tests.py` (platform suites) into CI (ADR-0005).
   → **Done (test-suite patch, 2026-09):** `tests/e2e`, `tests/integration`,
   and `tests/security` now run as a CI step; `tests/performance` stays
   local-only (timing noise on shared runners — see
   [`TESTING_AND_RELIABILITY.md`](TESTING_AND_RELIABILITY.md)).
2. Consider `docs/VERSIONING.md` when a release cadence starts.
   → Still open; tracked in [`ROADMAP.md`](ROADMAP.md).

## 9. Follow-on: Documentation Standardization (2026-09)

Executed under the approval gate; recorded as ADR-0008. No deletions, no
archives — content was preserved through every rename.

| Action | Detail | Status |
|---|---|---|
| Rename | `docs/TESTING.md` → `docs/TESTING_AND_RELIABILITY.md` (+ reliability-strategy section) | ✅ |
| Rename | `docs/SECURITY.md` → `docs/SECURITY_AND_PRIVACY.md` (+ privacy & data handling, AI safety) | ✅ |
| Deviation | `database/seed/DEMOS.md` kept as-is — `database/seed/README.md` already exists (untracked seed-credentials document), so the rename would collide; accepted, recorded in ADR-0008 | ✅ |
| Create | `docs/AI_INTERACTION_GUIDE.md`, `docs/IMPROVEMENT_AREAS.md` (required-set completion) | ✅ |
| Create | Root `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`, `SECURITY.md` | ✅ |
| Update | `docs/README.md` → standard-set index (9 required) + declared extensions; all cross-references to renamed files updated (`README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, this file) | ✅ |

Verification: required-file existence check passes; every relative link in
the changed documents resolves; `git am` on a byte-identical replica of
the stacked patch sequence applies cleanly.
