# ADR-0002 — One evaluation protocol for every system

- **Status:** Accepted (2026-10-07)

## Context
SE(3)-LVIO outputs IMU-frame poses. GrandTour ground truth is a total-station prism. A 38 cm lever arm
separates the two (measured in the pre-repo ARC-6 analysis). lightning-lm also outputs IMU-frame poses.

## Decision
- **Frame:** every estimate is converted to the prism frame with the SE(3)-LVIO `tools/to_prism.py`:
  `T_imu_prism` from the mission `/tf_static` plus the fixed lever-arm correction (−5.7, 1.8, −11.4) mm.
- **ATE:** follows the COMFORT/Codabench scorer.
  - evo `point_distance` APE, rigid alignment, no scale correction.
  - Pairing uses `t_max = min(GT dt, est dt)/2 + 5 ms`, capped at 50 ms.
  - Implemented once, in `lvx/evaluate.py`.
- **Time offsets:** per-mission IMU offsets are fixed in `configs/missions.yaml` and used by both systems.
- **Reporting:** RMSE, median and max are all reported, plus the pose coverage (estimate poses per LiDAR
  scan), so a run that loses half its poses can't look good. The GT pairing ratio first used here sits
  near 0.55 even for a perfect run; [ADR-0011](ADR-0011-pose-coverage.md) replaced it.

## Consequences
- A per-system fitted lever arm would make ATE look better (0.85 → 0.45 cm on ARC-6, pre-repo). It is
  deliberately **not** used, because it fits the metric rather than the system.
- Changing any of this needs a new ADR and a rerun of EXP-000.
