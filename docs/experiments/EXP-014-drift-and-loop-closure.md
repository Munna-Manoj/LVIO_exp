# EXP-014 — Is there drift worth closing loops for?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P5 (Camera and backend) · **System:** `se3-lvio` + `lightning-lm` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
**Terms used on this page**

| Term | Meaning |
|---|---|
| **ATE** | Absolute trajectory error: the root-mean-square distance between the estimated trajectory and the ground-truth trajectory, in centimetres, after the two are aligned. Lower is better. |
| **scan time (ms_p95)** | The time a system needs to process one LiDAR scan, in milliseconds. `ms_p95` is the 95th percentile over a mission: 95 % of the scans take less than this. |
| **noise floor** | The smallest ATE difference that counts as a real effect: 2 × σ, where σ is the standard deviation of ATE between identical runs of that system's stock config (EXP-000 for SE(3)-LVIO and lightning-lm, EXP-022 for GenZ-LIO). It is never less than 0.01 cm. |
| **variant** | One configuration that is run. Each variant differs from the variant it is compared with in exactly one change. |
| **dev missions** | The three missions used to decide experiments: ARC-6 (indoor, with smoke), EIG-2 (a glacier climb, outdoor) and SNOW-3 (a snow field, outdoor). The test missions are kept for final reports. |
| **`lightning`** | lightning-lm's config `lightning_indoor`: upstream's settings with 0.2 m grids. It is the better of lightning-lm's two configs on ARC-6 in EXP-000 (1.41 cm against 1.64 cm). |
| **lightning-lm on the field missions** | Both lightning-lm configs lose track on EIG-2 and SNOW-3 in EXP-000 (`lightning`: 294 cm and 41 cm). A lightning-lm variant is therefore judged on ARC-6 only. Its EIG-2 and SNOW-3 numbers are still reported. |
| **`baseline` (S9c)** | SE(3)-LVIO's full config `se3lvio_S9c`: S9b plus the online backend (plane bundle adjustment and iSAM2). It is SE(3)-LVIO's COMFORT leaderboard config. |
| **loop closure** | Recognising a place seen before and adding a constraint between the two visits, so that accumulated drift is removed. |
| **`lightning` with its backend** | lightning-lm also has loop closure and a pose graph. The LIO runner used in this study does not run them; EXP-014 adds them. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Loop closure is added to its backend. |
| GenZ-LIO | no | GenZ-LIO has no backend to add loop closure to. |
| lightning-lm | yes | lightning-lm's own loop closure is switched on. |

| | |
|---|---|
| **Question** | How much does each system drift without loop closure, and does adding loop closure reduce ATE? |
| **Hypothesis** | On short indoor missions the drift is millimetres, and SE(3)-LVIO's plane bundle adjustment already closes small loops. Loop closure helps only on long missions that revisit places. |
| **Prediction** | SE(3)-LVIO: ATE changes by less than the noise floor on ARC-6; better only on long missions with revisits (to be identified). lightning-lm, on ARC-6: ATE changes by less than the noise floor. |
| **Falsified if** | Loop closure improves ATE by more than the noise floor on a mission without revisits. That would mean the loop factor does something other than close loops. |
| **Decision rule** | Each system is run with and without loop closure (SE(3)-LVIO: `loop_closure` with it, `baseline` without it; lightning-lm: `lightning_loop` with it, `lightning` without it). On each mission, the side with loop closure is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. Loop closure helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. Loop closure hurts a system if the side with it is worse on any mission. For lightning-lm only ARC-6 is judged: loop closure helps lightning-lm if the side with it is better on ARC-6 with less than 10 % more ms_p95, and hurts lightning-lm if it is worse on ARC-6. Verdict: adopt if loop closure helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S9c`, unchanged |
| `loop_closure` | SE(3)-LVIO | `baseline` | SE(3)-LVIO S9c: loop closure added to the backend (candidates by distance, checked by point-to-plane alignment, added as a factor in iSAM2) |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_loop` | lightning-lm | `lightning` | lightning-lm: its own loop closure and pose graph switched on |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-014`.
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
lvx run EXP-014 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-014                  # runs.csv + summary.json
lvx figures EXP-014
lvx viewer EXP-014                # on the host: map + trajectories for the 3D viewer
lvx report EXP-014
```
<!-- lvx:end reproduce -->
