# EXP-022 — TODO the question as a title, e.g. How wide should the point-to-plane gate be?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P0 (Foundation: baselines and noise floor) · **System:** `genz-lio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | How much does ATE vary between identical runs of GenZ-LIO stock on the dev missions, and does the harness run it without dropping scans or mis-placing the LiDAR? |
| **Hypothesis** | GenZ-LIO's worker threads (correspondence search and map updates, runtime.max_threads 4) combine their results in a fixed order on an offline replay, as SE(3)-LVIO's frontend does (EXP-000), so its runs are deterministic or nearly so. With upstream's Hesai template and the GrandTour extrinsic it tracks every dev mission at centimetre level. |
| **Prediction** | σ(ATE) per mission below 0.05 cm. Every run has pose_coverage ≥ 0.99. ATE on ARC-6 below 3 cm. EXP-021 ran the same config without the IMU offset and got 1.382 (arc-6), 2.506 (eig-2) and 5.884 cm (snow-3); with the offset we expect each within ±20 % of those, since the offset is 5-6.5 ms and the IMU prior is only one input to each scan's update. |
| **Falsified if** | any run has pose_coverage below 0.99, any run fails, or ARC-6 ATE is 3 cm or more. Each means the harness or the config is wrong for GenZ-LIO (frame, extrinsic, timestamps, or core budget). |
| **Decision rule** | pass (verdict adopt = GenZ-LIO runs correctly in the harness, under the full protocol) if all 15 runs are ok with pose_coverage ≥ 0.99 and the ARC-6 mean ATE is below 3 cm; otherwise reject and fix the runner or config before any experiment uses GenZ-LIO. The σ per mission from this experiment is GenZ-LIO's noise floor for all later experiments (ADR-0004, ADR-0012). |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | genz_stock as is |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 5 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_median_cm`, `ate_max_cm`, `ms_mean`, `ms_p95`, `rss_mb`, `pose_coverage`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-022`.
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
lvx run EXP-022 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-022                  # runs.csv + summary.json
lvx figures EXP-022
lvx viewer EXP-022                # on the host: map + trajectories for the 3D viewer
lvx report EXP-022
```
<!-- lvx:end reproduce -->
