# EXP-015 — Does GNC protect the pose graph from false loops?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P6 (Stress tests) · **System:** `se3-lvio` · **Depends on:** EXP-014
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | With 1-3 injected false loop closures, does GNC (gtsam::GncOptimizer) keep ATE at the clean level where plain Huber does not? |
| **Hypothesis** | A single false loop can bend a pose graph; GNC-TLS is designed for exactly this case (poor initial guess for the outlier factor, high leverage). |
| **Prediction** | Huber: ATE grows with injected loops. GNC: within noise of the clean run. |
| **Falsified if** | GNC also degrades beyond noise with one injected loop. |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S9c as is |
| `huber_pgo` | loop factors with Huber kernel |
| `gnc_pgo` | loop factors solved with GncOptimizer (TLS) |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Stress profile:** `false-loops-3`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-015`.
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
lvx run EXP-015 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-015                  # runs.csv + summary.json
lvx figures EXP-015
lvx report EXP-015
```
<!-- lvx:end reproduce -->
