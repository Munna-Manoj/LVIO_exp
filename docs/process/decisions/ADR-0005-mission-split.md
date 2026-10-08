# ADR-0005 — Tune on dev, report on test

- **Status:** Accepted (2026-10-08, M0.5). Proposed 2026-10-07.

## Context
- **Twelve COMFORT missions have IMU time offsets** in SE(3)-LVIO (`imu_dt.yaml`).
- **Six of them have public prism ground truth** in the GrandTour HuggingFace release: ARC-3, ARC-6, CON-3, EIG-2,
  SNOW-3 and SPX-1. The other six are the COMFORT Test missions; the benchmark hides their ground truth.
- **The split is slightly contaminated already.** SE(3)-LVIO's defaults were tuned before this repo, on the six
  ground-truth missions.

## Decision
- **Split the six ground-truth missions** in `configs/missions.yaml`, three each. One mission per site goes to each
  side, and both sides cover indoor, outdoor and stairs:

  | Split | Missions | What they cover | Duration |
  |---|---|---|---|
  | `dev` | ARC-6, EIG-2, SNOW-3 | indoor with smoke; mountain outdoor with stairs; snow | 933 s |
  | `test` | ARC-3, CON-3, SPX-1 | indoor+outdoor multi-floor; construction site; outdoor metal stairs | 1883 s |

- **Choose variants on `dev`.** Run `test` once per concluded P-phase, to confirm.
- **Missions without ground truth** (split `nogt`) are used only for runtime and qualitative maps.

## Consequences
- **Reports state the contamination.** Every report's "Threats to validity" says that the defaults saw all six
  ground-truth missions.
- **`test` is twice as long as `dev`** and includes two multi-floor indoor/outdoor missions. Expect larger errors
  there; compare variants within a split, never across splits.
- **The split is fixed.** Moving a mission between splits needs a new ADR, and invalidates earlier `test` claims.
