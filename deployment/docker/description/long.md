AMAP (Accessible Multimodal Assembly Platform) is an enterprise-grade
cyber-physical manufacturing interface for workers with physical and
cognitive diversities. Workers drive the same workflow through optical
hand gestures, voice commands, or conventional input — chosen per worker,
adapted to their body, and gated by one authorization model regardless of
channel.

Everything obeys a strict four-stage invariant:
**Recognition ≠ Intent ≠ Authorization ≠ Execution**. MediaPipe hand
tracking and on-device Vosk speech-to-text (English + Hindi) capture raw
input; temporal fusion and dwell accumulation confirm intent while
filtering involuntary tremors; multi-tenant JWT + RBAC with PostgreSQL
row-level security enforce boundaries; and safety-critical actions require
secondary interlocks before execution. No audio or video ever leaves the
machine.

## Features

- Optical gesture recognition (palm, pinch, thumbs up/down, point, fist) with 300–1500 ms dwell smoothing
- Streaming voice commands (English + Hindi) against a bounded safety vocabulary
- Cross-modal fusion: reinforcing, complementary (point + command), conflict resolution with emergency-stop priority
- Evidence-based per-worker adaptation: dwell times, target sizes, gesture mappings
- Multi-role portals: worker workstation, supervisor telemetry, admin studio
- WCAG 2.1 AA interface verified by automated tests; 20/20 security audit criteria automated

## Quick Start

```bash
git clone https://github.com/Vijay-S-dev/AMAP.git
cd AMAP
docker compose up -d --build
curl http://localhost:8000/api/v1/health
```

The stack starts PostgreSQL 16, applies all migrations, seeds demo data,
and serves the API on port 8000 and the web app on port 3000.

## Documentation

Full documentation, architecture deep-dives, and the API contract:
https://github.com/Vijay-S-dev/AMAP/tree/main/docs
