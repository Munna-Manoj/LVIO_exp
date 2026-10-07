# EXP-009 — Does the coupled SE(3) retraction matter?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P4 (State formulation) · **System:** `se3-lvio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does replacing the SE(3) exponential retraction with the separate SO(3)×R³ retraction (FAST-LIO style) change ATE? |
| **Hypothesis** | For per-scan corrections (mm, mrad) the two retractions differ by about ½ φ×ρ, which is micrometres; any effect should appear only in fast turns or with large rotation uncertainty. |
| **Prediction** | Within noise on every dev mission; if anything, a difference on the fastest-turning segments. |
| **Falsified if** | SO(3)×R³ worse beyond noise on most missions (would support the paper's central claim more strongly than the theory predicts). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `so3xr3` | retraction SO(3)×R³ instead of SE(3) exp |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-009`.
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
lvx run EXP-009 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-009                  # runs.csv + summary.json
lvx figures EXP-009
lvx report EXP-009
```
<!-- lvx:end reproduce -->
