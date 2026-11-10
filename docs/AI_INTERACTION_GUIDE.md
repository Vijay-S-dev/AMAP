# AI Interaction Guide

Rules of engagement for AI agents (and automated tooling generally) working
on the AMAP codebase. The theme: agents may propose anything, but verified
tests and the human approval gate decide what lands.

## Agent boundaries

- **Code is truth.** When documentation and code disagree, the code wins;
  the agent's job is to update the documentation to match, not the reverse.
- **Never weaken a gate to make it pass.** Tests, coverage floors
  (`--cov-fail-under=85`), security checks, and CI steps are fixed
  contracts. If something legitimately must change, propose it explicitly
  with rationale (an ADR), do not quietly edit thresholds.
- **Preserve the platform invariant.** Any change touching the
  Recognition → Intent → Authorization → Execution pipeline must keep the
  four stages separate. In particular: recognition/AI components never
  authorize or execute, and safety-critical actions keep their secondary
  confirmation interlock.
- **No secrets in prompts, code, logs, or commits.** Secrets come from the
  environment (`.env.example` documents them); demo credentials
  (`SecurePassword123!`) are development-only and never used in production
  paths.
- **Data boundaries.** The codebase processes hand landmarks and speech
  on-device; do not introduce external API calls for camera, audio, or
  transcript data (see [`SECURITY_AND_PRIVACY.md`](SECURITY_AND_PRIVACY.md)).
- **Windows-safe patches.** No case-only file renames (ADR-0007); patches
  must apply with `git am` on NTFS checkouts.
- **Approval gate for destructive operations.** File deletions, moves,
  archives, and renames are proposed as a plan first and executed only
  after explicit user approval. Empty files and byte-identical duplicates
  are the only deletion candidates; anything possibly useful is archived.

## Local testing enforcement

**Before any commit or push**, the agent verifies locally — at minimum:

```bash
# Backend (requires migrated + seeded PostgreSQL, DATABASE_URL set)
cd backend && pytest -q

# Frontend
cd frontend && npm run typecheck && npm run lint && npm run test:engine
```

Rules:

- **Test failures block the commit.** Fix the code or the test (with
  justification) — never skip, deselect, or mark expected-failure to get
  green.
- **Security findings halt for manual review.** The 20 audit criteria
  (`backend/tests/test_security_audit_all_20.py`) must stay at 20/20.
- **New code lands with tests**, in the pyramid's unit layer first
  (see [`TESTING_AND_RELIABILITY.md`](TESTING_AND_RELIABILITY.md)).
- **Docs are synchronized** before the commit (see triggers below).
- CI re-runs everything on push; a red CI run invalidates the local
  verification and must be fixed before anything else proceeds.

## Documentation triggers

Each document has a binding update trigger; the agent updates it in the
same change that trips the trigger:

| Document | Update when |
|---|---|
| Root `README.md` | Setup, features, or usage change |
| [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) | Capabilities or audience change |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Major refactors, component/data flow changes |
| [`TESTING_AND_RELIABILITY.md`](TESTING_AND_RELIABILITY.md) | Testing, coverage, or CI policy changes |
| [`SECURITY_AND_PRIVACY.md`](SECURITY_AND_PRIVACY.md) | Security or privacy-relevant code changes |
| [`REFACTORING_PLAN.md`](REFACTORING_PLAN.md) | A tracked refactor task progresses |
| [`IMPROVEMENT_AREAS.md`](IMPROVEMENT_AREAS.md) | A gap is opened, closed, or re-assessed |
| [`ROADMAP.md`](ROADMAP.md) | Priorities or milestones change |
| Root `CHANGELOG.md` | Every user-visible change, at merge time |
| [`DECISIONS.md`](DECISIONS.md) | An architecture decision is made (new ADR) |

## Failure handling summary

| Situation | Agent action |
|---|---|
| Tests fail | Block the commit; fix root cause; no skips, no threshold edits |
| Security issue | Halt; surface for manual review; do not proceed with the change |
| Documentation gap | Generate the missing sections in the same change |
| Docs/code sync conflict | Code is truth; update the docs |
| Ambiguity about scope | Ask; the approval gate applies |
