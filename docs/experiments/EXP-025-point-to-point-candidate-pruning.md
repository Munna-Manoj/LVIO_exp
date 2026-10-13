# EXP-025 — TODO the question as a title, e.g. How wide should the point-to-plane gate be?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `genz-lio` · **Depends on:** EXP-022
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | GenZ-LIO keeps 128 point-to-point candidates per root voxel and divides the budget by 4 per subdivision. Does keeping more or fewer change ATE or only time? |
| **Hypothesis** | The nearest candidate is almost always among the ones kept, so the thinning saves time without losing matches. Keeping far fewer starts to miss the nearest match. |
| **Prediction** | No thinning (ratio 1) and 512 candidates: within noise, higher ms_p95. 32 candidates: worse on EIG-2 and SNOW-3, where the point-to-point residual carries more of the update. |
| **Falsified if** | no thinning or 512 candidates is better beyond noise on most missions (the stock budget loses matches). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. An SE(3)-LVIO arm follows only if EXP-024 adopts the point-to-point fallback. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | GenZ-LIO | – | the stock config `genz_stock`, unchanged |
| `ratio_1` | GenZ-LIO | `baseline` | reduction_ratio 1 (stock 4): children keep the parent's budget |
| `cand_32` | GenZ-LIO | `baseline` | max_points_per_voxel 32 (stock 128) |
| `cand_512` | GenZ-LIO | `baseline` | max_points_per_voxel 512 (stock 128) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_mean`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-025`.
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
lvx run EXP-025 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-025                  # runs.csv + summary.json
lvx figures EXP-025
lvx viewer EXP-025                # on the host: map + trajectories for the 3D viewer
lvx report EXP-025
```
<!-- lvx:end reproduce -->
