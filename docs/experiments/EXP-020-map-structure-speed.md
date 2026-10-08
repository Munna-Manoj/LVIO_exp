# EXP-020 — Does the map data structure set the speed of SE(3)-LVIO?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `se3-lvio` · **Depends on:** EXP-000, EXP-016
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | If SE(3)-LVIO's probabilistic VoxelMap is replaced by an iVox-style hashed voxel map with on-the-fly 5-NN plane fitting (as in Faster-LIO / lightning-lm), how do ms/scan and ATE change? |
| **Hypothesis** | VoxelMap pays for plane covariance (eigen-decomposition and covariance updates per voxel) but gives better residual weights; iVox makes insertion and lookup cheaper (O(1) hashing, no plane refits) but its constant-weight planes are noisier. Speed and accuracy should trade against each other. |
| **Prediction** | iVox variant: ms_p95 lower by 20-40 %, ATE worse beyond noise on most dev missions (weights matter more than lookup cost at 2000 inliers). |
| **Falsified if** | the iVox variant is not faster beyond timing noise, or is both faster and at least as accurate (map structure would then be a free speedup). |
| **Decision rule** | report a trade-off: adopt only if ms_p95 drops by more than 10 % AND ATE is within 2σ noise on every dev mission; reject if ATE is worse beyond 2σ on any mission; otherwise inconclusive with the measured speed/accuracy trade-off. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `ivox` | map backend iVox (hashed voxels, 5-NN plane fit, covariance from the fit residual) instead of VoxelMap |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ms_p95`, secondary `ms_mean`, `rss_mb`, `ate_rmse_cm`, `ate_max_cm`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-020`.
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
lvx run EXP-020 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-020                  # runs.csv + summary.json
lvx figures EXP-020
lvx viewer EXP-020                # on the host: map + trajectories for the 3D viewer
lvx report EXP-020
```
<!-- lvx:end reproduce -->
