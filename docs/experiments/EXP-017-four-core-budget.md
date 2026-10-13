# EXP-017 — Do both systems hold 10 Hz and 20 Hz on four cores?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P7 (Embedded real time) · **System:** `se3-lvio` + `lightning-lm` + `genz-lio` · **Depends on:** EXP-016
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | With 4 pinned cores, what are ms/scan p95 and max for SE(3)-LVIO (S8, S9b), lightning-lm and GenZ-LIO? |
| **Hypothesis** | Both fit 10 Hz on 4 server cores; lightning-lm has more headroom for 20 Hz. Pi 5 cores are ~2-3× slower, so the server margin must be large. |
| **Prediction** | S8 p95 < 50 ms; lightning p95 < 30 ms; S9b over 50 ms. GenZ-LIO p95 below 100 ms on every dev mission but above 50 ms on EIG-2 and SNOW-3 (EXP-022: 38, 66 and 61 ms). |
| **Falsified if** | S8 p95 > 100 ms on 4 cores (not real time even on server cores). |
| **Decision rule** | report only (no adopt/reject): verdict inconclusive unless a system exceeds 100 ms p95, then reject that system for 10 Hz on this host. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `s9b` | SE(3)-LVIO | – | swap baseline config to S9b |
| `ll_indoor` | lightning-lm | – | swap baseline config to lightning-lm indoor |
| `genz` | GenZ-LIO | – | swap baseline config to GenZ-LIO stock (the reference of the GenZ-LIO arms) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
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
lvx viewer EXP-017                # on the host: map + trajectories for the 3D viewer
lvx report EXP-017
```
<!-- lvx:end reproduce -->
