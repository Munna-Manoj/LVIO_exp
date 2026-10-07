# EXP-018 — Which design choices matter when the data gets worse?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P6 (Stress tests) · **System:** `both` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Under controlled degradation (drop Livox, drop 10-30 % of scans, 4× point thinning, ±5 ms IMU time shift), how do both systems degrade? |
| **Hypothesis** | SE(3)-LVIO is tuned for clean data and degrades faster under scan drops; lightning-lm's guards make it degrade gracefully. |
| **Prediction** | lightning-lm degrades less in relative terms under scan drops; SE(3)-LVIO remains more accurate in absolute terms. |
| **Falsified if** | SE(3)-LVIO degrades less in relative terms under every profile. |
| **Decision rule** | report only: verdict inconclusive with a degradation table; feeds the choice of P2 guards. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `ll_indoor` | swap baseline config to lightning-lm indoor |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Stress profile:** `suite-v1`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-018`.
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
lvx run EXP-018 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-018                  # runs.csv + summary.json
lvx figures EXP-018
lvx report EXP-018
```
<!-- lvx:end reproduce -->
