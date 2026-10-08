# EXP-005 — Does projecting out degenerate directions help SE(3)-LVIO?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P2 (Filter safeguards) · **System:** `se3-lvio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does lightning-lm-style degeneracy handling (eigen-analysis of HᵀH, update only well-constrained directions) improve ATE? |
| **Hypothesis** | In corridors and open areas some pose directions are weakly constrained; updating them only adds noise. The IMU prior already damps them, so gains should be small and local. |
| **Prediction** | Within noise on indoor missions; better on missions with long corridors or open terrain. |
| **Falsified if** | worse beyond noise on any mission (projection throws away real information). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `degen_proj` | project the update onto eigen-directions with λ > λ_min |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-005`.
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
lvx run EXP-005 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-005                  # runs.csv + summary.json
lvx figures EXP-005
lvx viewer EXP-005                # on the host: map + trajectories for the 3D viewer
lvx report EXP-005
```
<!-- lvx:end reproduce -->
