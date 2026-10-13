# EXP-016 — How much accuracy does each millisecond buy?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P7 (Embedded real time) · **System:** `se3-lvio` + `genz-lio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | How do ATE and ms/scan change as the adaptive downsampling target moves from 500 to 4000 inliers? |
| **Hypothesis** | Accuracy saturates once planes are well covered; time grows roughly linearly with inliers. |
| **Prediction** | ATE flat from 1000 to 4000, worse at 500; ms_p95 roughly linear. GenZ-LIO, the same factors on its N_min/N_max: ATE flat from ×0.5 to ×2, worse at ×0.25; ms_p95 roughly linear. |
| **Falsified if** | ATE keeps improving beyond 2000 (the default is under-sampled). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. Applied to each system separately: SE(3)-LVIO's arms against `baseline`, GenZ-LIO's against `genz`, each with its own noise floor (EXP-000, EXP-022). The verdict is adopt if the rule adopts for both systems, reject if it rejects for both, otherwise inconclusive; the TL;DR gives both (ADR-0012 addendum). |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `n500` | SE(3)-LVIO | `baseline` | downsample target 500 inliers (baseline 2000) |
| `n1000` | SE(3)-LVIO | `baseline` | downsample target 1000 inliers (baseline 2000) |
| `n3000` | SE(3)-LVIO | `baseline` | downsample target 3000 inliers (baseline 2000) |
| `n4000` | SE(3)-LVIO | `baseline` | downsample target 4000 inliers (baseline 2000) |
| `genz` | GenZ-LIO | – | swap baseline config to GenZ-LIO stock (the reference of the GenZ-LIO arms) |
| `genz_x0p25` | GenZ-LIO | `genz` | GenZ-LIO point budget ×0.25 (N_min/N_max 250/1000, stock 1000/4000) |
| `genz_x0p5` | GenZ-LIO | `genz` | GenZ-LIO point budget ×0.5 (N_min/N_max 500/2000, stock 1000/4000) |
| `genz_x1p5` | GenZ-LIO | `genz` | GenZ-LIO point budget ×1.5 (N_min/N_max 1500/6000, stock 1000/4000) |
| `genz_x2` | GenZ-LIO | `genz` | GenZ-LIO point budget ×2 (N_min/N_max 2000/8000, stock 1000/4000) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ms_mean`, `ms_p95`, `rss_mb`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-016`.
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
lvx run EXP-016 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-016                  # runs.csv + summary.json
lvx figures EXP-016
lvx viewer EXP-016                # on the host: map + trajectories for the 3D viewer
lvx report EXP-016
```
<!-- lvx:end reproduce -->
