# EXP-000 — How large is run-to-run noise, and do the pre-repo baselines reproduce?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P0 (Foundation: baselines and noise floor) · **System:** `both` · **Depends on:** none
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | How much does ATE vary between identical runs of each baseline, and do the pre-repo ARC-6 numbers reproduce inside the harness? |
| **Hypothesis** | Multithreaded map updates (OpenMP) make runs non-deterministic; the spread is small but not zero, and it sets the smallest effect any later experiment may claim. |
| **Prediction** | σ(ATE) per baseline and mission below 0.05 cm; ARC-6 means within 3σ of the pre-repo numbers (S8 0.81, S9a 0.89, S9b 0.90, S9c 0.90, lightning stock 1.64, indoor 1.41 cm). |
| **Falsified if** | any baseline misses its pre-repo number by more than 3σ, which means the harness changed the system (wrong config, frame or time offset). |
| **Decision rule** | pass (verdict adopt = the harness is trusted) if every baseline reproduces within 3σ; otherwise reject and fix the harness before any other experiment runs. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `s9a` | swap baseline config to S9a (adds Livox) |
| `s9b` | swap baseline config to S9b (adds camera) |
| `s9c` | swap baseline config to S9c (adds backend) |
| `ll_stock` | swap baseline config to lightning-lm stock |
| `ll_indoor` | swap baseline config to lightning-lm indoor grid |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 5 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_median_cm`, `ate_max_cm`, `ms_mean`, `ms_p95`, `rss_mb`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-000`.
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
lvx run EXP-000 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-000                  # runs.csv + summary.json
lvx figures EXP-000
lvx report EXP-000
```
<!-- lvx:end reproduce -->
