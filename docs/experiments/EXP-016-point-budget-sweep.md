# EXP-016 — How much accuracy does each millisecond buy?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P7 (Embedded real time) · **System:** `se3-lvio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | How do ATE and ms/scan change as the adaptive downsampling target moves from 500 to 4000 inliers? |
| **Hypothesis** | Accuracy saturates once planes are well covered; time grows roughly linearly with inliers. |
| **Prediction** | ATE flat from 1000 to 4000, worse at 500; ms_p95 roughly linear. |
| **Falsified if** | ATE keeps improving beyond 2000 (the default is under-sampled). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `n500` | downsample target 500 inliers (baseline 2000) |
| `n1000` | downsample target 1000 inliers (baseline 2000) |
| `n3000` | downsample target 3000 inliers (baseline 2000) |
| `n4000` | downsample target 4000 inliers (baseline 2000) |

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
lvx report EXP-016
```
<!-- lvx:end reproduce -->
