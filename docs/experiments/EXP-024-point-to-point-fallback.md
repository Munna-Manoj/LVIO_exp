# EXP-024 — TODO the question as a title, e.g. How wide should the point-to-plane gate be?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `se3-lvio` + `genz-lio` · **Depends on:** EXP-000, EXP-022
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does GenZ-LIO's hybrid-metric update (a point that fits no plane gets a point-to-point residual, weighted by λ_po) improve ATE, in both systems? |
| **Hypothesis** | In open scenes many points fall in voxels with no plane; they carry information that point-to-plane alone throws away. In confined scenes almost every point has a plane, so the fallback rarely fires. |
| **Prediction** | SE(3)-LVIO: within noise on ARC-6, better on EIG-2 and SNOW-3. GenZ-LIO without it: within noise on ARC-6, worse on EIG-2 and SNOW-3. |
| **Falsified if** | the side with point-to-point residuals is not better on either open mission in either system. |
| **Decision rule** | Per system, against its own reference and noise floor (EXP-000, EXP-022): the point-to-point fallback helps if, on at least 2/3 of the missions, the side with it beats the side without it by more than 2σ (SE(3)-LVIO: `p2p_fallback` better than `baseline`; GenZ-LIO: `genz_no_hybrid` worse than `genz`) and no mission goes the other way beyond 2σ; it hurts if any mission goes the other way beyond 2σ. Verdict adopt (add it to SE(3)-LVIO) if it helps in both systems and SE(3)-LVIO's ms_p95 grows by less than 10 %; reject if it hurts in either; otherwise inconclusive. The TL;DR gives both systems (ADR-0012 addendum). |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `p2p_fallback` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: point-to-point residual for points without a plane, λ_po 0.05 |
| `genz` | GenZ-LIO | – | swap baseline config to GenZ-LIO stock (the reference of the GenZ-LIO arms) |
| `genz_no_hybrid` | GenZ-LIO | `genz` | GenZ-LIO: point-to-plane only (hybrid_metric.enable false) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `inliers_mean`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-024`.
<!-- lvx:end results -->

TODO up to 5 observations, each pointing at a table cell or figure.

## Discussion

TODO why it happened; link the theory in docs/explain/.

## Verdict

TODO adopt / reject / inconclusive, citing the decision rule.

## Threats to validity

TODO what could make this conclusion wrong.

## Failures

TODO failed or dirty runs and why (or "none").

## Reproduce

<!-- lvx:begin reproduce -->
```bash
lvx run EXP-024 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-024                  # runs.csv + summary.json
lvx figures EXP-024
lvx viewer EXP-024                # on the host: map + trajectories for the 3D viewer
lvx report EXP-024
```
<!-- lvx:end reproduce -->
