# EXP-001 — How wide should the point-to-plane residual gate be?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P1 (Outliers and robustness) · **System:** `se3-lvio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Is the hard 3σ point-to-plane gate the right width, or does a tighter/looser gate change ATE? |
| **Hypothesis** | The IMU prior is good enough that 3σ already separates inliers; tighter gates lose good constraints, looser gates admit smoke and clutter. |
| **Prediction** | 2.5σ-4σ within noise of 3σ; 2σ worse (fewer inliers), 5σ slightly worse on smoky ARC-6. |
| **Falsified if** | a gate other than 3σ improves ATE beyond 2σ noise on most missions. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `gate_2p0` | residual gate 2.0σ (baseline 3.0σ) |
| `gate_2p5` | residual gate 2.5σ (baseline 3.0σ) |
| `gate_4p0` | residual gate 4.0σ (baseline 3.0σ) |
| `gate_5p0` | residual gate 5.0σ (baseline 3.0σ) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `inliers_mean`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-001`.
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
lvx run EXP-001 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-001                  # runs.csv + summary.json
lvx figures EXP-001
lvx report EXP-001
```
<!-- lvx:end reproduce -->
