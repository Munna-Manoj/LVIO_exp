# ADR-0004 — Effects must exceed run-to-run noise

- **Status:** Accepted (2026-10-07)

## Context
OpenMP map updates make runs non-deterministic. On ARC-6 the pre-repo configurations differ by
≈0.01 cm, which may well be pure noise.

## Decision
- **EXP-000** measures σ(ATE) per baseline and mission, with ≥5 repeats.
- **Effect threshold:** a variant's effect on a mission counts only if |Δ mean ATE| > 2σ. Otherwise
  it is reported as "within noise". `lvx/evaluate.py` applies this (`NOISE_K = 2`).
- **Spread:** reports always show mean ± std over repeats, per mission.

## Consequences
- Small "improvements" disappear. That's the point.
- σ is per (baseline, mission), so a noisy mission doesn't hide effects on quiet ones.
- If σ is ~0 (deterministic runs), a 0.005 cm floor applies (the resolution of the GT is coarser).
