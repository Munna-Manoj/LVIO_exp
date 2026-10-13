# EXP-020 — Does the map data structure set the speed?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `se3-lvio` + `lightning-lm` · **Depends on:** EXP-000, EXP-016
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
| **`lightning`** | lightning-lm's config `lightning_indoor`: upstream's settings with 0.2 m grids. It is the better of lightning-lm's two configs on ARC-6 in EXP-000 (1.41 cm against 1.64 cm). |
| **lightning-lm on the field missions** | Both lightning-lm configs lose track on EIG-2 and SNOW-3 in EXP-000 (`lightning`: 294 cm and 41 cm). A lightning-lm variant is therefore judged on ARC-6 only. Its EIG-2 and SNOW-3 numbers are still reported. |
| **VoxelMap** | SE(3)-LVIO's map: each voxel stores a plane and the plane's uncertainty, refitted as points arrive. |
| **iVox** | lightning-lm's map: a hash table of voxels that stores points; a plane is fitted to a scan point's 5 nearest map points at query time. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | VoxelMap is replaced by iVox. |
| GenZ-LIO | no | GenZ-LIO's map also keeps the point candidates its point-to-point residual needs. iVox has no such candidates, so the swap would be two changes. |
| lightning-lm | yes | iVox is replaced by VoxelMap. |

| | |
|---|---|
| **Question** | SE(3)-LVIO stores planes with their uncertainty in a VoxelMap; lightning-lm stores points in iVox and fits a plane to the 5 nearest points on the fly. If each system gets the other's map, how do scan time and ATE change? |
| **Hypothesis** | VoxelMap pays for each plane's uncertainty (an eigen-decomposition and covariance update per voxel) but gives better residual weights. iVox makes insertion and lookup cheaper (hashing, no plane refits) but its equally weighted planes are noisier. Speed and accuracy trade against each other. |
| **Prediction** | SE(3)-LVIO with iVox: ms_p95 20 to 40 % lower, and ATE worse by more than the noise floor on at least two dev missions. lightning-lm with VoxelMap, on ARC-6: ms_p95 higher and ATE better. |
| **Falsified if** | SE(3)-LVIO with iVox is not faster beyond timing noise, or it is both faster and at least as accurate (the map structure would then be a free speed-up). |
| **Decision rule** | A speed and accuracy trade-off, judged for each system. SE(3)-LVIO: adopt iVox if it cuts ms_p95 by more than 10 % and ATE is within the noise floor on every dev mission; reject if ATE is worse by more than the noise floor on any mission; otherwise inconclusive, with the measured trade-off. lightning-lm (ARC-6 only): adopt VoxelMap if ATE is better by more than the noise floor with less than 20 % more ms_p95; reject if ATE is worse; otherwise inconclusive. Verdict: adopt if both systems adopt their variant, reject if both reject, and inconclusive otherwise. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `ivox` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: iVox map (hashed voxels, plane fit to the 5 nearest points, covariance from the fit residual) instead of VoxelMap |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_voxelmap` | lightning-lm | `lightning` | lightning-lm: VoxelMap (planes with uncertainty) instead of iVox |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ms_p95`, secondary `ms_mean`, `rss_mb`, `ate_rmse_cm`, `ate_max_cm`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-020`.
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
lvx run EXP-020 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-020                  # runs.csv + summary.json
lvx figures EXP-020
lvx viewer EXP-020                # on the host: map + trajectories for the 3D viewer
lvx report EXP-020
```
<!-- lvx:end reproduce -->
