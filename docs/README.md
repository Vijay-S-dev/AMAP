# AMAP Documentation Index

Start here: the root [`README.md`](../README.md) covers quickstart, usage,
configuration, and deployment. This index maps the deeper documentation.

## Standard set (required)

| # | Document | Contents |
|---|---|---|
| 1 | [`README.md`](README.md) | This index — the documentation entry point |
| 2 | [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md) | Goals, features, technology, audience, maturity |
| 3 | [`ARCHITECTURE.md`](ARCHITECTURE.md) | System structure, fusion + adaptation engines, multi-tenancy |
| 4 | [`AI_INTERACTION_GUIDE.md`](AI_INTERACTION_GUIDE.md) | Agent boundaries, local-test enforcement, doc update triggers |
| 5 | [`REFACTORING_PLAN.md`](REFACTORING_PLAN.md) | Tracked refactors: scope, execution, verification |
| 6 | [`TESTING_AND_RELIABILITY.md`](TESTING_AND_RELIABILITY.md) | Test pyramid, coverage policy, skip analysis, reliability strategy |
| 7 | [`IMPROVEMENT_AREAS.md`](IMPROVEMENT_AREAS.md) | Known gaps, limitations, technical debt |
| 8 | [`SECURITY_AND_PRIVACY.md`](SECURITY_AND_PRIVACY.md) | Security practices, privacy & data handling, AI safety, reporting |
| 9 | [`ROADMAP.md`](ROADMAP.md) | Priority-based future improvement plan |

## Declared extensions

Project-specific specifications, indexed here per the documentation
contract (ADR-0008):

| Document | Contents |
|---|---|
| [`MASTER_SPEC.md`](MASTER_SPEC.md) | Master specification |
| [`API_CONTRACT.md`](API_CONTRACT.md) | REST API contract |
| [`AI.md`](AI.md) | AI perception/intent subsystem specification |
| [`VOICE_ARCHITECTURE.md`](VOICE_ARCHITECTURE.md) | Vosk streaming voice pipeline |
| [`DATABASE.md`](DATABASE.md) | Database schema and migrations |
| [`Backend.md`](Backend.md) | Backend conventions and change log |
| [`DECISIONS.md`](DECISIONS.md) | Architecture Decision Records (ADRs) |

`VERSIONING.md` does not exist yet — it will be added (not created
speculatively) when a release cadence starts; see [`ROADMAP.md`](ROADMAP.md).

## Historical

- [`archive/`](archive/) — superseded documents, read-only reference
- [`prompts/`](prompts/) — development workflow prompts (extension group)

## Root-level documents

| Document | Contents |
|---|---|
| [`../README.md`](../README.md) | Project overview, setup, usage |
| [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | Contribution guide and PR process |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Notable changes, Keep a Changelog format |
| [`../SECURITY.md`](../SECURITY.md) | Vulnerability reporting policy |
| [`../CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) | Community standards |
| [`../LICENSE`](../LICENSE) | MIT License |
