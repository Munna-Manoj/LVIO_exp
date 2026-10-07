# EXP-010 — Does estimating accelerometer bias and gravity online pay off?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P4 (State formulation) · **System:** `se3-lvio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does the 17-dim state (with accel bias and S2 gravity) beat a 12-dim state with them fixed after initialisation, as in lightning-lm? |
| **Hypothesis** | Accel bias and gravity direction are weakly observable but matter when the start is not static; fixing them saves compute and removes a source of drift-by-misestimation. |
| **Prediction** | Within noise on missions with a static start; 17-dim better on missions that start moving. |
| **Falsified if** | 12-dim better beyond noise on most missions. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `state12` | freeze ba and gravity after initialisation (zero their process noise and gain) |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-010`.
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
lvx run EXP-010 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-010                  # runs.csv + summary.json
lvx figures EXP-010
lvx report EXP-010
```
<!-- lvx:end reproduce -->
