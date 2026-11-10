# Decision Log (ADR)

Short, dated records of structural decisions. Newest last.

---

## ADR-0001 — Repository layout stays a backend/frontend monorepo (2026-11-10)

**Context:** A generic `src/ + tests/ + config/` layout was proposed during
the file-organization refactor.

**Decision:** Keep the existing structure — `backend/` (layered FastAPI:
routes → services → repositories → models), `frontend/` (Next.js
feature-organized), `database/`, `deployment/`, `docs/`, `scripts/`,
`tests/` (platform-level), `ai/`.

**Rationale:** The layout is already conventional for a full-stack monorepo.
Moving to `src/` would break the Docker build contexts, CI paths,
`PYTHONPATH=/app/backend`, pytest/tsconfig configuration, and every import —
high risk, zero functional gain.

## ADR-0002 — Single source of truth for configuration copies (2026-11-10)

**Decision:** Remove duplicate/stale copies of configuration that had
accumulated in `docs/`: `BACKEND REQS` (stale subset of
`backend/requirements.txt`), `PYTEST.INI` (duplicate of
`backend/pytest.ini`), `ENV.EXAMPLES` (stale subset of `.env.example`),
`docs/.GITIGNORE` (subset of the root `.gitignore`), and `frontend/package`
+ `frontend/tsconfig` (stale duplicates of `package.json` /
`tsconfig.json`).

**Rationale:** Divergent copies mislead contributors; the canonical files
are the ones the tooling actually reads.

## ADR-0003 — `docs/REQUIREMENTS.md` removed (2026-11-10)

**Decision:** Delete the empty `docs/REQUIREMENTS.md`.

**Rationale:** It was a placeholder that was never filled;
`docs/MASTER_SPEC.md` is the canonical requirements/specification document.

## ADR-0004 — Root `shared/` scaffolding removed (2026-11-10)

**Decision:** Remove the empty root-level `shared/{constants,schemas,types}`
directories (`.gitkeep` only).

**Rationale:** Unreferenced by any code — frontend code imports the
`frontend/shared/` module via the `@/shared` alias. Dead scaffolding
confuses contributors.

## ADR-0005 — Root `tests/` retained; still manually run (2026-11-10)

**Decision:** Keep the platform-level suites (`tests/e2e`, `tests/integration`,
`tests/performance`, `tests/security`) at the repository root, wired through
`scripts/run_all_tests.py`.

**Rationale:** They test the whole platform cross-cuttingly, not a single
package. **Follow-up candidate:** add them to CI.

## ADR-0006 — Documentation contract (2026-11-10)

**Decision:** Root keeps `README.md` + `LICENSE` only. `docs/` keeps the
living documents; historical/superseded documents move to
`docs/archive/docs-backup-YYYY-MM-DD/`. `SECURITY.md`, `TESTING.md`, and this
log are maintained as living documents.

## ADR-0007 — Keep `docs/Backend.md` name as-is (2026-11-10)

**Context:** Renaming `docs/Backend.md` to `docs/BACKEND.md` was proposed for
naming consistency with the other CAPS-named documents.

**Decision:** Do not do the case-only rename.

**Rationale:** Case-only renames cannot be applied with `git am`/`git apply`
on case-insensitive filesystems (Windows NTFS, macOS default): the
destination path "already exists" because it is the same file. Renaming
would require every Windows contributor to perform manual steps, for a purely
cosmetic gain. The file keeps its historical name.

## ADR-0008 — Documentation standardization contract (2026-09)

**Context:** The documentation had grown organically: a strong root README
and a mixed `docs/` set, but no index, no agent rules, no changelog, and
two near-miss names (`SECURITY.md`, `TESTING.md`) against the adopted
standard set.

**Decision:** Adopt a documentation contract. Root keeps exactly:
`README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
`CHANGELOG.md`, `SECURITY.md`. `docs/` holds the 9-file standard set
(`README`, `PROJECT_OVERVIEW`, `ARCHITECTURE`, `AI_INTERACTION_GUIDE`,
`REFACTORING_PLAN`, `TESTING_AND_RELIABILITY`, `IMPROVEMENT_AREAS`,
`SECURITY_AND_PRIVACY`, `ROADMAP`) plus **declared extensions**: any
additional file is allowed if and only if it is listed with a one-line
purpose in the `docs/README.md` index. `VERSIONING.md` is created only
when a release cadence starts. Superseded material goes to
`docs/archive/docs-backup-YYYY-MM-DD/`. Subdirectories use `README.md`
(not other ALL-CAPS names) for local documentation. **Accepted
deviation:** `database/seed/DEMOS.md` keeps its name — the `README.md`
name in that directory is already occupied by an existing (uncommitted)
seed-credentials document, so the rename would collide on the primary
development machine.

**Rationale:** The standard set makes maintainability visible (what exists,
what is missing, what each doc's update trigger is) while declared
extensions keep the project's substantial specifications
(`MASTER_SPEC.md`, `API_CONTRACT.md`, `AI.md`, `VOICE_ARCHITECTURE.md`,
`DATABASE.md`, `Backend.md`, `DECISIONS.md`) in place instead of forcing
lossy merges. Renames preserved content and updated every cross-reference;
no deletions were needed. Executed under the approval gate: the full plan
(merges, moves, renames, creations) was presented and approved before any
file changed.
