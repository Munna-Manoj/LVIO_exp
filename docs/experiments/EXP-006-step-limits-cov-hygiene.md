# EXP-006 — Do update safeguards change accuracy, or only robustness?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P2 (Filter safeguards) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-000
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
| **`baseline` (S8)** | SE(3)-LVIO's stock config `se3lvio_S8`: one LiDAR (the Hesai XT32) and the IMU, no camera, no backend. |
| **`genz`** | GenZ-LIO's stock config `genz_stock`: upstream's Hesai settings, with only the sensor calibration and the 4-core limit set. |
| **`lightning`** | lightning-lm's config `lightning_indoor`: upstream's settings with 0.2 m grids. It is the better of lightning-lm's two configs on ARC-6 in EXP-000 (1.41 cm against 1.64 cm). |
| **lightning-lm on the field missions** | Both lightning-lm configs lose track on EIG-2 and SNOW-3 in EXP-000 (`lightning`: 294 cm and 41 cm). A lightning-lm variant is therefore judged on ARC-6 only. Its EIG-2 and SNOW-3 numbers are still reported. |
| **the two safeguards** | (1) A step limit: an update that moves the pose by more than 0.5 m or 5° is rejected, and the pose stays at the IMU prediction. (2) Covariance hygiene: after every prediction and update, the covariance matrix is made symmetric and its diagonal is kept between 1e-9 and 100. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | The safeguards are added. |
| GenZ-LIO | yes | The safeguards are added. GenZ-LIO itself only checks that the state stays finite. |
| lightning-lm | yes | lightning-lm already has the safeguards; its variant switches them off. |

| | |
|---|---|
| **Question** | lightning-lm protects its filter with two safeguards. Do they change ATE on the dev missions? |
| **Hypothesis** | On healthy data the safeguards never trigger, so ATE does not change. They matter only under stress (EXP-018). |
| **Prediction** | All three systems: ATE identical, or changed by less than the noise floor, on every dev mission. |
| **Falsified if** | In any system, the side with the safeguards differs from the side without them by more than the noise floor on a dev mission. |
| **Decision rule** | Each system is run with and without the safeguards (SE(3)-LVIO: `guards` with it, `baseline` without it; GenZ-LIO: `genz_guards` with it, `genz` without it; lightning-lm: `lightning` with it, `lightning_no_guards` without it). On each mission, the side with the safeguards is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. The safeguards helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. The safeguards hurts a system if the side with it is worse on any mission. For lightning-lm only ARC-6 is judged: the safeguards helps lightning-lm if the side with it is better on ARC-6 with less than 10 % more ms_p95, and hurts lightning-lm if it is worse on ARC-6. Verdict: adopt if the safeguards helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. The prediction (no effect) holds if every comparison is within the noise floor. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `guards` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: both safeguards added |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_guards` | GenZ-LIO | `genz` | GenZ-LIO: both safeguards added |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_no_guards` | lightning-lm | `lightning` | lightning-lm: both safeguards switched off |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-006`.
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
lvx run EXP-006 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-006                  # runs.csv + summary.json
lvx figures EXP-006
lvx viewer EXP-006                # on the host: map + trajectories for the 3D viewer
lvx report EXP-006
```
<!-- lvx:end reproduce -->
