# Improvement Areas

Known gaps, limitations, and technical debt — the honest list, ordered
roughly by impact. Each item says what is missing, why it matters, and
where the work would land. Companion documents: [`ROADMAP.md`](ROADMAP.md)
(priorities and planned work) and [`TESTING_AND_RELIABILITY.md`](TESTING_AND_RELIABILITY.md)
(coverage detail).

## Testing

- **Supervisor service coverage (72%).** The largest service
  (`services/supervisor_service.py`, 441 statements) has untested
  multi-repository flows: task reassignment, escalation, and the
  report/export generators. Each needs five mocked repositories in
  sequence — mechanical but worth doing.
- **Supervisor route error mappings (76%).** The 404/403/400 translation
  branches of `routes/supervisor.py` are untested (happy paths covered);
  same pattern as the sessions-route tests that exist.
- **Performance suite outside CI.** `tests/performance` is local-only
  because shared runners produce noisy timings. Needs a timing-tolerant
  harness or a self-hosted runner before it can gate merges.

## Release & distribution

- **No tagged releases.** No version exists yet (backend reports `0.1.0`
  informally); no changelog history before 2026-09; badges for build
  status/version are static. Blocking: a versioning policy
  (see [`ROADMAP.md`](ROADMAP.md)).
- **No registry publishing.** Images build locally (`amap-backend:local`)
  only. Docker Hub descriptions are staged
  (`deployment/docker/description/`) and validated in CI, but nothing is
  pushed and no sync step exists.
- **Static badges.** README build/tests/coverage badges are hardcoded
  text; live GitHub Actions badges need the repository public (or at least
  reachable) and a version badge needs a release.

## Documentation

- **No screenshots or demo GIF.** The README describes three portals but
  shows none. Needs a running seeded stack, capture, and descriptive alt
  text (accessibility policy applies).
- **`docs/Backend.md` name inconsistency.** Mixed-case name kept
  deliberately (ADR-0007 — Windows `git am` cannot apply case-only
  renames). Cosmetic debt, accepted.

## Product / platform

- **Voice languages limited to English + Hindi.** Adding a language means
  a Vosk model tier, vocabulary normalization rules, and per-language
  tests; the pipeline is ready, the models are not provisioned.
- **Adaptation review workflow.** The split between auto-applied low-risk
  ergonomic changes and supervisor-queued review exists but is rough
  around the edges (approval UI, expiry of recommendations).
- **Single-worker gesture personalization.** Gesture-action mapping is
  per-worker with org presets; there is no cross-worker learning or
  org-level analytics yet.

## Infrastructure

- **Docker Desktop instability on the dev host.** The primary development
  machine (Windows + 8 GB RAM) has a flaky Docker engine on Insider build
  26300; workarounds are retry loops and BuildKit cache survival. Not a
  code issue, but it shapes how the stack is run locally.
- **Real-STT tests are opt-in locally.** They need ~1 GB of prefetched
  Vosk models (`scripts/prefetch_vosk_models.py`). CI always runs them;
  developers who skip the prefetch see 24 skips.

## Recently closed

- ~~Repository organization (obsolete files, empty placeholder docs)~~ —
  completed 2026-11-10, see [`REFACTORING_PLAN.md`](REFACTORING_PLAN.md).
- ~~Coverage gate missing~~ — CI now enforces 85% (baseline 90.5%).
- ~~Platform suites not in CI~~ — `tests/e2e, integration, security` run
  in CI; the stale multimodal test they caught is fixed.
- ~~Documentation standardization~~ — this set: root contract + 9-file
  `/docs/` standard adopted (ADR-0008).
