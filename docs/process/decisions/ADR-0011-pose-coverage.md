# ADR-0011 — Report pose coverage, not the GT pairing ratio

- **Status:** Accepted (2026-10-08). Amends the "Reporting" line of ADR-0002; ATE itself is unchanged.

## Context
- **The pairing ratio was meant to catch dropped poses.** ADR-0002 reported it, so that a run which loses half
  its poses can't look good. It was `n_pair / n_gt`.
- **It sits near 0.55 even for a perfect run.** GrandTour prism ground truth arrives every 44 ms (median, the
  same on all six ground-truth missions). Both systems output one pose per 10 Hz LiDAR scan, and the COMFORT
  pairing window is about 27 ms. So only about every second GT pose can ever be paired.
- **Measured on ARC-6** (SE(3)-LVIO S8, 2026-10-08):
  - 3490 estimate poses for the 3491 scans inside the IMU span, so coverage is 0.9997;
  - 1752 of 3173 GT poses paired, a ratio of 0.55.
- **It doesn't track pose loss.** A run that drops half its poses changes the ratio for unrelated reasons.

## Decision
- **Report `pose_coverage` instead:** estimate poses divided by the LiDAR scans a system can process, which are
  the scans inside the IMU's time span (`lvx/evaluate.py` `usable_scans`). 1.0 means one pose per scan, and
  dropped poses lower it directly.
  - On five of the six missions, the GrandTour IMU stops about 12 s before the LiDAR: ARC-6 has 3611 scans, of
    which 3491 fall inside the IMU span.
  - Counting all scans would put coverage at 0.967 for a run that dropped nothing.
- **Keep the raw counts:** `n_pair`, `n_gt`, `n_est` and `n_scans` stay in `runs.csv`.
- **Leave ATE, the pairing rule and the alignment unchanged.** They still follow the COMFORT scorer.

## Consequences
- **Coverage can exceed 1.0** if a system ever outputs more than one pose per scan. Report it as measured.
- **GT gaps don't affect coverage.** The total station loses the prism for long stretches; ARC-3 has 464 s of
  gaps in 713 s. Those gaps limit what ATE can see, not coverage.

## Alternatives considered
- **Widen the pairing window so more GT poses pair.** Rejected: it changes ATE, so the numbers would no longer
  match the COMFORT scorer.
- **Divide by the GT poses an ideal 10 Hz estimate could pair.** Rejected: it gives the same information as
  coverage, but is harder to explain and depends on the GT timestamps.
