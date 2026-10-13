# EXP-007 — Does dropping weak, close returns remove smoke without hurting accuracy?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `se3-lvio` + `genz-lio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does removing points with intensity < 3 within 3 m before matching reduce smoke-induced error? |
| **Hypothesis** | ARC-6 smoke points are low-intensity (median 2 vs 11), short-range (1.5 m) and transient; they enter the map as fake planes. |
| **Prediction** | Better on ARC-6 near the start, within noise elsewhere. GenZ-LIO: the same as SE(3)-LVIO (the filter is applied to the same Hesai points before preprocessing). |
| **Falsified if** | worse beyond noise on missions without smoke (real dark surfaces removed). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. Applied to each system separately: SE(3)-LVIO's arms against `baseline`, GenZ-LIO's against `genz`, each with its own noise floor (EXP-000, EXP-022). The verdict is adopt if the rule adopts for both systems, reject if it rejects for both, otherwise inconclusive; the TL;DR gives both (ADR-0012 addendum). |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `smoke_i3_r3` | SE(3)-LVIO | `baseline` | drop intensity < 3 within 3 m |
| `genz` | GenZ-LIO | – | swap baseline config to GenZ-LIO stock (the reference of the GenZ-LIO arms) |
| `genz_smoke_i3_r3` | GenZ-LIO | `genz` | GenZ-LIO: drop intensity < 3 within 3 m |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-007`.
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
lvx run EXP-007 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-007                  # runs.csv + summary.json
lvx figures EXP-007
lvx viewer EXP-007                # on the host: map + trajectories for the 3D viewer
lvx report EXP-007
```
<!-- lvx:end reproduce -->
