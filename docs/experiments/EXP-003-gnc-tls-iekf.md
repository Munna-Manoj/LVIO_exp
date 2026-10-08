# EXP-003 — Does GNC-TLS annealed across IEKF iterations help?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P1 (Outliers and robustness) · **System:** `se3-lvio` · **Depends on:** EXP-002
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does graduated non-convexity with a truncated-least-squares cost, annealed over the 4-6 IEKF iterations, beat a fixed gate and a fixed robust kernel? |
| **Hypothesis** | GNC helps when outliers are many and the start is poor; with a good IMU prior it should match the gate on clean data and only help where outliers are dense. |
| **Prediction** | Within noise of the best of EXP-002 on clean missions; better only under the P6 dynamic-clutter stress profile. |
| **Falsified if** | GNC-TLS is worse beyond noise on clean missions (annealing too slow for 5 iterations) AND not better under stress. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `gnc_tls` | GNC-TLS weights, μ annealed ×1.4 per iteration |
| `gnc_tls_8it` | GNC-TLS with max_iter 8 so the schedule can finish |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-003`.
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
lvx run EXP-003 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-003                  # runs.csv + summary.json
lvx figures EXP-003
lvx viewer EXP-003                # on the host: map + trajectories for the 3D viewer
lvx report EXP-003
```
<!-- lvx:end reproduce -->
