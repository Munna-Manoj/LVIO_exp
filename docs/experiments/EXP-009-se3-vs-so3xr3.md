# EXP-009 — Does the coupled SE(3) retraction matter?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P4 (State formulation) · **System:** `se3-lvio` + `genz-lio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does replacing the SE(3) exponential retraction with the separate SO(3)×R³ retraction (FAST-LIO style) change ATE? |
| **Hypothesis** | For per-scan corrections (mm, mrad) the two retractions differ by about ½ φ×ρ, which is micrometres; any effect should appear only in fast turns or with large rotation uncertainty. |
| **Prediction** | Within noise on every dev mission; if anything, a difference on the fastest-turning segments. GenZ-LIO is SO(3)×R³ natively, so its arm goes the other way (SO(3)×R³ → SE(3)); within noise too. |
| **Falsified if** | SO(3)×R³ worse beyond noise on most missions (would support the paper's central claim more strongly than the theory predicts). |
| **Decision rule** | Per system, against its own reference and noise floor (EXP-000, EXP-022): SE(3) is better if, on at least 2/3 of the missions, the SE(3) side beats the SO(3)×R³ side by more than 2σ (SE(3)-LVIO: `so3xr3` worse than `baseline`; GenZ-LIO: `genz_se3` better than `genz`) and no mission goes the other way beyond 2σ. Verdict adopt (the coupled retraction matters) if SE(3) is better in both systems; reject (it does not) if every mission is within 2σ in both systems; otherwise inconclusive. The TL;DR gives both systems (ADR-0012 addendum). |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `so3xr3` | SE(3)-LVIO | `baseline` | retraction SO(3)×R³ instead of SE(3) exp |
| `genz` | GenZ-LIO | – | swap baseline config to GenZ-LIO stock (the reference of the GenZ-LIO arms) |
| `genz_se3` | GenZ-LIO | `genz` | GenZ-LIO: retraction SE(3) exp instead of its SO(3)×R³ |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
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
lvx viewer EXP-009                # on the host: map + trajectories for the 3D viewer
lvx report EXP-009
```
<!-- lvx:end reproduce -->
