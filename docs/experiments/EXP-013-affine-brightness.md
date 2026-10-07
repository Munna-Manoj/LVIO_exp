# EXP-013 — Does affine brightness compensation help the photometric update?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P5 (Camera and backend) · **System:** `se3-lvio` · **Depends on:** EXP-004
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does estimating a per-frame affine brightness (a, b) improve S9b under lighting change? |
| **Hypothesis** | Brightness constancy is violated under smoke and changing light; FAST-LIVO2 estimates exposure for this reason. |
| **Prediction** | Better than S9b on missions with lighting change, within noise elsewhere. |
| **Falsified if** | within noise on every mission. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S9b as is |
| `affine_ab` | per-frame affine brightness (a, b) in the photometric residual |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-013`.
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
lvx run EXP-013 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-013                  # runs.csv + summary.json
lvx figures EXP-013
lvx report EXP-013
```
<!-- lvx:end reproduce -->
