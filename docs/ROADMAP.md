# AMAP Roadmap

Public priorities, kept aligned with the Roadmap section of the root
[`README.md`](../README.md). Items are ordered by current intent, not by
commitment dates. Last reviewed: 2026-09.

## Recently completed

- Repository organization refactor (docs, archive, obsolete-file removal) — see [`REFACTORING_PLAN.md`](REFACTORING_PLAN.md)
- Test-suite hardening: coverage gate at 85% (baseline 90.5%), platform
  suites in CI, 54 new contract tests, skipped-test analysis — see [`TESTING_AND_RELIABILITY.md`](TESTING_AND_RELIABILITY.md)
- Streaming voice pipeline (Vosk, EN + HI) with configurable model tiers
- Worker gesture-action personalization resolved from PostgreSQL
  (personal override → org preset → canonical default)
- Professional README with usage, configuration, Docker, and API docs

## In progress / next

1. **Supervisor-service coverage push.** `services/supervisor_service.py`
   sits at 72% — the remaining blocks are multi-repository operational
   flows (task reassignment, escalation, report generators). Documented in
   [`TESTING_AND_RELIABILITY.md`](TESTING_AND_RELIABILITY.md).
2. **Versioning policy and tagged releases.** Adds `docs/VERSIONING.md`
   when a release cadence starts (follow-up from the org refactor); enables
   live CI and version badges in the README.
3. **Container registry publishing.** Images currently build locally
   (`amap-backend:local`). Docker Hub descriptions are already staged at
   `deployment/docker/description/` and validated in CI
   (`scripts/validate_docker_description.py`); publishing also needs a
   sync step (API or CI) to push the descriptions to the registry listing.

## Under consideration

- **README visuals:** real screenshots of the three portals and a demo GIF
  (none exist today; keep alt text descriptive per accessibility policy).
- **Performance suite in CI:** currently local-only because shared runners
  produce noisy timings; needs a timing-tolerant harness or self-hosted
  runner.
- **Voice language expansion** beyond English and Hindi (new Vosk models,
  vocabulary normalization, and tests per language).
- **Adaptation review workflow polish:** clearer split between
  auto-applied low-risk ergonomic changes and queued supervisor review.

## Known limitations

- No tagged releases; API/schema may change without notice until v1.
- Images are not published to a registry; deployments build from source.
- The performance suite is timing-sensitive and best run on idle hardware
  (`python scripts/run_all_tests.py`).
- Real-STT tests require ~1 GB of prefetched Vosk models; they always run
  in CI but are opt-in locally.
