# ADR-0005 — Tune on dev, report on test

- **Status:** Proposed (2026-10-07). Accepted once M0.5 fixes the mission lists.

## Context
- Twelve COMFORT missions exist; only the six Validation missions have public ground truth.
- SE(3)-LVIO's defaults were tuned on all six Validation missions (pre-repo), so any split is
  already slightly contaminated.

## Decision
- Split the six GT missions into `dev` (3) and `test` (3) in `configs/missions.yaml`, covering
  indoor, outdoor and stairs on both sides where possible.
- Variants are chosen on `dev`. `test` is run once per concluded P-phase to confirm.
- Missions without GT are used only for runtime and qualitative maps.

## Consequences
- The contamination is stated in every report's "Threats to validity".
- Moving a mission between splits needs a new ADR, and invalidates earlier `test` claims.
