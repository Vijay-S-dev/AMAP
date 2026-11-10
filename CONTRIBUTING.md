# Contributing to AMAP

Thank you for improving the Accessible Multimodal Assembly Platform. This
guide covers the practical path from change to merged PR. Agent/automation
rules live in [`docs/AI_INTERACTION_GUIDE.md`](docs/AI_INTERACTION_GUIDE.md);
architecture decisions are recorded in [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Getting set up

Follow the [Quickstart](README.md#quickstart) in the README, then confirm
your environment is healthy:

```bash
cd backend && pytest -q                 # 876 passed, 24 skipped expected without Vosk models
cd ../frontend && npm run test:engine   # 142 tests
```

## Before you open a pull request

1. **Branch** from `main`; keep changes focused — one logical change per PR.
2. **Install the hooks** (recommended): `pip install pre-commit && pre-commit install`.
3. **Run the gates locally** — CI runs all of them again:
   ```bash
   # Backend (needs a migrated + seeded PostgreSQL; see README Configuration)
   cd backend && pytest -q
   # Frontend
   cd frontend && npm run typecheck && npm run lint && npm run test:engine && npm run build
   ```
4. **Add or update tests** for any behavior change, in the unit layer first
   ([testing guide](docs/TESTING_AND_RELIABILITY.md)). New modules should
   not land under 80% coverage; the CI gate fails under 85% total.
5. **Update the docs** whose trigger your change trips (table in
   [`docs/AI_INTERACTION_GUIDE.md`](docs/AI_INTERACTION_GUIDE.md)) and add
   a line to the root [`CHANGELOG.md`](CHANGELOG.md).

## Non-negotiables

- **The invariant:** Recognition ≠ Intent ≠ Authorization ≠ Execution.
  Recognition/AI code never authorizes or executes; safety-critical
  actions keep their secondary confirmation interlock.
- **Security stays at 20/20.** The audit criteria in
  `backend/tests/test_security_audit_all_20.py` must keep passing.
  Parameterized SQL only; secrets only via environment.
- **Privacy:** no external API calls for camera, audio, or transcript
  data — processing stays on-device
  ([`docs/SECURITY_AND_PRIVACY.md`](docs/SECURITY_AND_PRIVACY.md)).
- **Accessibility:** WCAG 2.1 AA (48px targets, focus visibility,
  screen-reader semantics) is enforced by tests; keep it that way.
- **Windows-safe changes:** no case-only file renames (ADR-0007); patches
  and merges must work on NTFS checkouts.

## Pull request process

1. Open the PR against `main` with a description covering **what, why, and
   how it was tested**.
2. CI must be fully green: backend tests + 85% coverage floor, platform
   suites, E2E, frontend gates, compose smoke.
3. Request review; significant architectural changes should reference (or
   add) an ADR in [`docs/DECISIONS.md`](docs/DECISIONS.md).
4. Squash-merge keeps history readable; the commit message documents any
   files deleted or archived.

## Reporting bugs and security issues

- Bugs: [GitHub Issues](https://github.com/Vijay-S-dev/AMAP/issues)
- Security: privately to the maintainers — see [`SECURITY.md`](SECURITY.md).
  Please do not open public issues for security reports.
