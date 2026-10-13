# EXP-026 — TODO the question as a title, e.g. How wide should the point-to-plane gate be?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** PX (Cross-system comparison) · **System:** `genz-lio` · **Depends on:** EXP-022
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | With the same dev-split tuning budget SE(3)-LVIO had, how close does GenZ-LIO get? |
| **Hypothesis** | Most of the SNOW-3 gap to SE(3)-LVIO S8 (5.602 vs 1.265 cm) comes from the state and map design, not from tuning; tuning closes at most a third of it. |
| **Prediction** | No variant brings SNOW-3 below 4.2 cm (a third of the gap); the best variant within 0.3 cm of genz_stock on ARC-6. |
| **Falsified if** | a tuned GenZ-LIO matches SE(3)-LVIO S8 within noise on SNOW-3. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | GenZ-LIO | – | the stock config `genz_stock`, unchanged |
| `lambda_po_0p02` | GenZ-LIO | `baseline` | λ_po 0.02 (stock 0.05) |
| `lambda_po_0p2` | GenZ-LIO | `baseline` | λ_po 0.2 (stock 0.05) |
| `voxel_0p5` | GenZ-LIO | `baseline` | root voxel 0.5 m (stock 1.0) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-026`.
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
lvx run EXP-026 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-026                  # runs.csv + summary.json
lvx figures EXP-026
lvx viewer EXP-026                # on the host: map + trajectories for the 3D viewer
lvx report EXP-026
```
<!-- lvx:end reproduce -->
