# EXP-008 — Should the map be updated every scan or only at keyframes?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-000
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
| **keyframe** | A scan taken after the robot has moved more than 1 m or turned more than 2° since the last keyframe (lightning-lm's `kf_dis_th` and `kf_angle_th`). |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Keyframe-only map updates are added. |
| GenZ-LIO | yes | Keyframe-only map updates are added. |
| lightning-lm | yes | lightning-lm already updates its map only at keyframes; its variant adds every scan. |

| | |
|---|---|
| **Question** | Does adding scans to the map only at keyframes, as lightning-lm does, change ATE and scan time? |
| **Hypothesis** | Adding every scan gives a denser map, but it also adds passing objects and costs time. Adding only keyframes gives a sparser map and saves time. |
| **Prediction** | SE(3)-LVIO and GenZ-LIO with keyframe-only updates: slightly worse ATE (sparser planes) and lower ms_p95. GenZ-LIO saves more time than SE(3)-LVIO, because its map update also refreshes the point-to-point candidates. lightning-lm with every-scan updates, on ARC-6: slightly better ATE and higher ms_p95. |
| **Falsified if** | In SE(3)-LVIO or GenZ-LIO, keyframe-only updates improve ATE by more than the noise floor on at least two dev missions. |
| **Decision rule** | Each system is run with and without keyframe-only map updates (SE(3)-LVIO: `kf_insert` with it, `baseline` without it; GenZ-LIO: `genz_kf_insert` with it, `genz` without it; lightning-lm: `lightning` with it, `lightning_every_scan` without it). On each mission, the side with keyframe-only map updates is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. Keyframe-only map updates helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. Keyframe-only map updates hurts a system if the side with it is worse on any mission. For lightning-lm only ARC-6 is judged: keyframe-only map updates helps lightning-lm if the side with it is better on ARC-6 with less than 10 % more ms_p95, and hurts lightning-lm if it is worse on ARC-6. Verdict: adopt if keyframe-only map updates helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `kf_insert` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: add scans to the map only at keyframes |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_kf_insert` | GenZ-LIO | `genz` | GenZ-LIO: add scans to the map only at keyframes |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_every_scan` | lightning-lm | `lightning` | lightning-lm: add every scan to the map |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`, `rss_mb`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-008`.
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
lvx run EXP-008 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-008                  # runs.csv + summary.json
lvx figures EXP-008
lvx viewer EXP-008                # on the host: map + trajectories for the 3D viewer
lvx report EXP-008
```
<!-- lvx:end reproduce -->
