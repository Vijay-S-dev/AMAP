# AMAP Project Overview

A one-page summary of what AMAP is, kept in sync with the root
[`README.md`](../README.md). Last reviewed: 2026-09.

## Identity

**AMAP — Accessible Multimodal Assembly Platform** (a.k.a. Hybrid Control
Interface) is an enterprise-grade cyber-physical manufacturing interface
for workers with physical and cognitive diversities. It lets a worker on
an assembly line drive the same workflow through optical hand gestures,
voice commands, or conventional input — chosen per worker, adapted to
their body, and gated by one authorization model regardless of channel.

## Problem

Manufacturing execution software assumes able-bodied interaction: precise
clicks, small targets, steady hands. Workers with tremors, limited motor
range, or cognitive load constraints are forced to adapt to the tool
instead of the tool adapting to them — which costs productivity, safety,
and dignity.

## Approach

Every input channel flows through the same four-stage invariant
(**Recognition ≠ Intent ≠ Authorization ≠ Execution**):

1. **Recognition** — MediaPipe optical hand tracking (in-browser) and
   on-device Vosk streaming speech-to-text (English + Hindi) capture raw
   input; nothing leaves the machine.
2. **Intent** — cross-modal temporal fusion, fuzzy keyword normalization,
   and dwell accumulation turn noisy signals into confirmed intent while
   filtering involuntary tremors.
3. **Authorization** — multi-tenant JWT + RBAC with PostgreSQL row-level
   security enforce organization boundaries.
4. **Execution** — safety-critical actions require secondary interlocks
   before dispatch; everything is audit-logged immutably.

An evidence-based adaptation engine tunes the interaction to each worker
(dwell times, target sizes, gesture mappings) only after repeated
difficulty signals — never on single outliers.

## Who it serves

| Audience | What they get |
|---|---|
| **Workers** (primary) | Accessible multimodal workstation: HUD, dwell timers, voice + gesture control, assistance calling |
| **Supervisors** | Real-time line telemetry, worker status, assistance escalation/resolution |
| **Admins** | Organization presets, adaptation review/approval, immutable audit trail |
| **Researchers / integrators** | A tested, documented platform for accessible-manufacturing research |

## Capability summary

- Optical gesture recognition: palm, pinch, thumbs up/down, point, open
  hand, fist — with 300–1500 ms dwell smoothing
- Streaming voice commands (EN + HI) against a bounded safety vocabulary
- Cross-modal fusion: reinforcing, complementary (point + command), and
  conflict-resolution strategies with safety overrides (e-stop priority)
- Worker personalization: adaptation profiles + gesture-action mapping
- Multi-tenant security: PBKDF2, RLS, RBAC, rate limiting, 20/20 audited
- WCAG 2.1 AA interface, verified by automated tests
- 900 automated tests (876 backend + 24 CI-run STT) at 90.5% coverage,
  full CI gate including compose smoke tests

## Technology

FastAPI 0.115 (Python 3.11) · Next.js 14 (React 18, TypeScript) ·
PostgreSQL 16 · Vosk (on-device STT) · MediaPipe Tasks Vision ·
Docker Compose · GitHub Actions CI.

## Maturity

**Active development, pre-release.** Research-origin project evolving
toward a deployable platform. CI-gated main branch (tests, 85% coverage
floor, E2E, compose smoke); no tagged releases yet — schema and API may
change until v1. Current status and plans: [`ROADMAP.md`](ROADMAP.md).
