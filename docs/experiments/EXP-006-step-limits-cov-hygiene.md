# EXP-006 — Do step limits and covariance hygiene change accuracy or only robustness?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P2 (Filter safeguards) · **System:** `se3-lvio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Do lightning-lm-style guards (reject an update step > 0.5 m / 5°, symmetrise and floor the covariance) change ATE? |
| **Hypothesis** | These guards never trigger on healthy data, so they should not change accuracy; they matter only under stress (P6). |
| **Prediction** | Bit-identical or within noise on every dev mission; fewer divergences under the P6 scan-drop profile. |
| **Falsified if** | any change beyond noise on clean data (the guard triggers when it should not). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `guards` | step limit 0.5 m / 5° + covariance symmetrise and floor |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-006`.
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
lvx run EXP-006 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-006                  # runs.csv + summary.json
lvx figures EXP-006
lvx report EXP-006
```
<!-- lvx:end reproduce -->
