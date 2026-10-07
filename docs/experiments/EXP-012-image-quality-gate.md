# EXP-012 — Does skipping bad frames make the camera pay for itself?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P5 (Camera and backend) · **System:** `se3-lvio` · **Depends on:** EXP-004
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does skipping the photometric update on dark or low-texture frames improve the S9b configuration? |
| **Hypothesis** | Bad frames give biased photometric constraints; skipping them keeps good-frame information and saves time. |
| **Prediction** | S9b with the gate ≤ S9a ATE, lower ms_p95 than S9b. |
| **Falsified if** | no change beyond noise and no time saving. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S9b as is |
| `img_gate` | skip the update if mean intensity < 25 or gradient energy below the 10th percentile |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-012`.
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
lvx run EXP-012 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-012                  # runs.csv + summary.json
lvx figures EXP-012
lvx report EXP-012
```
<!-- lvx:end reproduce -->
