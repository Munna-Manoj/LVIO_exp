# EXP-023 — Should the point budget grow with the scene's size?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P7 (Embedded real time) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-000, EXP-022
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
| **point budget** | The number of LiDAR points a system keeps from each scan after downsampling. |
| **scene size** | GenZ-LIO's measure of how open the scene is: the average range of the scan's points, averaged over the last 5 scans. |
| **scene-scaled budget** | A target number of points that rises from 1000 at small scene size to 4000 once the scene size reaches 30 m. A controller adjusts the voxel size to meet it. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Its fixed target of 2000 points becomes scene-scaled. |
| GenZ-LIO | yes | GenZ-LIO is scene-scaled already; its variant uses a fixed 2000. |
| lightning-lm | yes | Its fixed voxel becomes a controller with the scene-scaled target. |

| | |
|---|---|
| **Question** | GenZ-LIO keeps more points per scan in open scenes than in confined ones. Does that beat a fixed budget, in each system? |
| **Hypothesis** | Confined scenes have many nearby planes, so few points constrain the pose well. Open scenes have few, distant planes and need more points. A fixed budget keeps too many points indoors (costing time) and too few outdoors (costing accuracy). |
| **Prediction** | Every system, with the scene-scaled budget: ATE changes by less than the noise floor on ARC-6, with lower ms_p95, and is better on EIG-2 and SNOW-3. lightning-lm is judged on ARC-6 only, so for lightning-lm the prediction is lower ms_p95 with ATE within the noise floor. |
| **Falsified if** | In no system is the side with the scene-scaled budget better on either EIG-2 or SNOW-3. |
| **Decision rule** | Each system is run with and without the scene-scaled budget (SE(3)-LVIO: `scale_aware` with it, `baseline` without it; GenZ-LIO: `genz` with it, `genz_fixed_2000` without it; lightning-lm: `lightning_scale_aware` with it, `lightning` without it). On each mission, the side with the scene-scaled budget is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. The scene-scaled budget helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. The scene-scaled budget hurts a system if the side with it is worse on any mission. For lightning-lm only ARC-6 is judged: the scene-scaled budget helps lightning-lm if the side with it is better on ARC-6 with less than 10 % more ms_p95, and hurts lightning-lm if it is worse on ARC-6. Verdict: adopt if the scene-scaled budget helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `scale_aware` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: target rises from 1000 points in confined scenes to 4000 in open ones (stock: a fixed 2000) |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_fixed_2000` | GenZ-LIO | `genz` | GenZ-LIO: a fixed target of 2000 points (stock: 1000 rising to 4000) |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_scale_aware` | lightning-lm | `lightning` | lightning-lm: a voxel size adjusted so that the target rises from 1000 points to 4000 (stock: a fixed 0.2 m voxel) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`, `ms_mean`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-023`.
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
lvx run EXP-023 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-023                  # runs.csv + summary.json
lvx figures EXP-023
lvx viewer EXP-023                # on the host: map + trajectories for the 3D viewer
lvx report EXP-023
```
<!-- lvx:end reproduce -->
