# EXP-000 — How large is run-to-run noise, and do the pre-repo baselines reproduce?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🔒 approved (pre-registered) · **Phase:** P0 (Foundation: baselines and noise floor) · **System:** `both` · **Depends on:** none
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | How much does ATE vary between identical runs of each baseline on the dev missions, and do the pre-repo ARC-6 numbers reproduce inside the harness? |
| **Hypothesis** | Multithreaded map updates (OpenMP) make runs non-deterministic; the spread is small but not zero, and it sets the smallest effect any later experiment may claim. |
| **Prediction** | σ(ATE) per baseline and mission below 0.05 cm. On ARC-6 every mean is within 3σ of the pre-repo number (S8 0.8055, S9a 0.8916, S9b 0.8976, S9c 0.8989, lightning stock 1.6391, indoor 1.4066 cm; recomputed with lvx.evaluate from the pre-repo estimates). EIG-2 and SNOW-3 have no pre-repo numbers; there EXP-000 measures σ and the baselines only. Every run has pose_coverage ≥ 0.99. |
| **Falsified if** | any baseline misses its pre-repo ARC-6 number by more than 3σ, or any run has pose_coverage below 0.99. Either means the harness changed the system (wrong config, frame, time offset or core budget). |
| **Decision rule** | pass (verdict adopt = the harness is trusted) if every baseline reproduces on ARC-6 within 3σ and every run has pose_coverage ≥ 0.99; otherwise reject and fix the harness before any other experiment runs. The σ per (baseline, mission) from this experiment is the noise floor for all later ones (ADR-0004). |

<sub>Fields above are pre-registered (`spec.lock`).</sub>
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
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_median_cm`, `ate_max_cm`, `ms_mean`, `ms_p95`, `rss_mb`, `pose_coverage`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `approved`). Numbers appear here after `lvx eval EXP-000`.
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
lvx viewer EXP-000                # on the host: map + trajectories for the 3D viewer
lvx report EXP-000
```
<!-- lvx:end reproduce -->
