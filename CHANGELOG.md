# Changelog

All notable changes to AMAP (Accessible Multimodal Assembly Platform) are
documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) once it starts
tagging releases (see `docs/ROADMAP.md` — until then, entries accumulate
under Unreleased).

## [Unreleased]

### Added

- Documentation standardization: root `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `CHANGELOG.md`, `SECURITY.md`;
  `docs/AI_INTERACTION_GUIDE.md`, `docs/IMPROVEMENT_AREAS.md`;
  `docs/README.md` documentation index; ADR-0008 records the adopted
  documentation contract.
- Docker Hub descriptions staged at `deployment/docker/description/`
  (short + long) with `scripts/validate_docker_description.py`, validated
  in CI.
- Professional README: table of contents, usage walkthrough (seeded demo
  login + API examples), configuration tables, Docker deployment, API
  reference, project status, roadmap; `docs/PROJECT_OVERVIEW.md` and
  `docs/ROADMAP.md`.
- CI: coverage gate (85%) on the backend suite; platform suites
  (`tests/e2e`, `tests/integration`, `tests/security`) run in CI.
- 54 backend tests: app configuration validation (24), work-session HTTP
  contract incl. heartbeat branches and every error mapping (16),
  assistance service ownership guards and pass-through (14);
  `routes/sessions.py` and `services/assistance_service.py` now at 100%
  coverage.
- `.pre-commit-config.yaml` with fast staged-file checks (optional).

### Changed

- `docs/TESTING.md` renamed to `docs/TESTING_AND_RELIABILITY.md` and
  extended with the reliability strategy; `docs/SECURITY.md` renamed to
  `docs/SECURITY_AND_PRIVACY.md` and extended with privacy and AI-safety
  sections (content preserved).
- README facts corrected: 53 migrations (was 24), 45 repositories (was 23),
  Node 20+ (was 18+), PostgreSQL 16+ (was 15+); `ai/`, `scripts/`,
  `tests/`, `deployment/` added to the architecture tree.
- `backend/requirements.txt` pins `pytest-cov` and `coverage`.

### Fixed

- Stale platform test: the multimodal spatial+voice integration test now
  sends the spatial context required by complementary fusion (it had been
  failing silently outside CI); its `contributing_modes` assertion is
  order-insensitive.

### Security

- No security-relevant changes pending release. Security policy:
  root `SECURITY.md`; practices: `docs/SECURITY_AND_PRIVACY.md`.
