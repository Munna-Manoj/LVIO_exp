# EXP-002 — Does a robust kernel in the IEKF update beat hard gating alone?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P1 (Outliers and robustness) · **System:** `se3-lvio` · **Depends on:** EXP-001
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does down-weighting residuals with Huber or Cauchy inside each IEKF iteration (IRLS) reduce ATE compared with gating alone? |
| **Hypothesis** | Residuals near the gate (partial occlusion, smoke edges, thin structure) are not fully wrong; smooth weights keep their information without letting them pull the estimate. |
| **Prediction** | Small gains (< 0.05 cm) on clean missions, larger on ARC-6 near smoke; Cauchy ≥ Huber. |
| **Falsified if** | neither kernel changes ATE beyond noise on any mission, or both make it worse. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `huber` | Huber IRLS weight, k = 1.345σ |
| `cauchy` | Cauchy IRLS weight, c = 2.385σ |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-002`.
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
lvx run EXP-002 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-002                  # runs.csv + summary.json
lvx figures EXP-002
lvx report EXP-002
```
<!-- lvx:end reproduce -->
