# EXP-019 — Is lightning-lm tuned fairly?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** PX (Cross-system comparison) · **System:** `lightning-lm` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | With the same dev-split tuning budget SE(3)-LVIO had, how close does lightning-lm get? |
| **Hypothesis** | Most of the 0.6-0.8 cm ARC-6 gap comes from map representation and residual weighting, not from tuning; tuning closes at most a third of it. |
| **Prediction** | Best lightning-lm variant within 0.3 cm of its indoor baseline. |
| **Falsified if** | a tuned lightning-lm matches SE(3)-LVIO S8 within noise. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | lightning_indoor as is |
| `grid_0p1` | 0.1 m scan/map/iVox grid |
| `icp_w_1000` | plane_icp_weight 1000 |
| `filter_1` | point_filter_num 1 |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-019`.
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
lvx run EXP-019 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-019                  # runs.csv + summary.json
lvx figures EXP-019
lvx report EXP-019
```
<!-- lvx:end reproduce -->
