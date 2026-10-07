# EXP-017 — Do both systems hold 10 Hz and 20 Hz on four cores?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P7 (Embedded real time) · **System:** `both` · **Depends on:** EXP-016
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | With 4 pinned cores, what are ms/scan p95 and max for SE(3)-LVIO (S8, S9b) and lightning-lm? |
| **Hypothesis** | Both fit 10 Hz on 4 server cores; lightning-lm has more headroom for 20 Hz. Pi 5 cores are ~2-3× slower, so the server margin must be large. |
| **Prediction** | S8 p95 < 50 ms; lightning p95 < 30 ms; S9b over 50 ms. |
| **Falsified if** | S8 p95 > 100 ms on 4 cores (not real time even on server cores). |
| **Decision rule** | report only (no adopt/reject): verdict inconclusive unless a system exceeds 100 ms p95, then reject that system for 10 Hz on this host. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `s9b` | swap baseline config to S9b |
| `ll_indoor` | swap baseline config to lightning-lm indoor |

- **Missions:** arc-6 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ms_p95`, secondary `ms_mean`, `ms_max`, `rss_mb`, `ate_rmse_cm`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-017`.
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
lvx run EXP-017 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-017                  # runs.csv + summary.json
lvx figures EXP-017
lvx report EXP-017
```
<!-- lvx:end reproduce -->
