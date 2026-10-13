# EXP-016 — How much accuracy does each millisecond of scan time buy?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P7 (Embedded real time) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-000
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
| **downsampling** | Thinning a scan by merging the points that fall in the same cube (voxel) of a grid. A larger voxel keeps fewer points. |
| **how each system sets its budget** | SE(3)-LVIO adjusts its voxel size after every scan so that about 2000 points match a plane. GenZ-LIO adjusts its voxel size so that it keeps 1000 points in confined scenes, rising to 4000 in open ones. lightning-lm uses a fixed 0.2 m voxel; on surfaces the number of points kept scales with 1 / voxel², so its voxel sizes are chosen to give about the same factors. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Its target number of points is swept: 500, 1000, 3000, 4000. |
| GenZ-LIO | yes | Its minimum and maximum are scaled together by 0.25, 0.5, 1.5 and 2. |
| lightning-lm | yes | Its fixed scan voxel is swept: 0.40, 0.28, 0.16, 0.14 m. |

| | |
|---|---|
| **Question** | When each system keeps fewer or more points per scan, how do its ATE and its scan time change? |
| **Hypothesis** | More points give the system more planes to align each scan to, so ATE falls as the point budget grows. Beyond some budget, the scan is already aligned as well as the data allow: ATE stops falling, while scan time keeps growing roughly in proportion to the number of points. |
| **Prediction** | SE(3)-LVIO: compared with its stock 2000 points, ATE changes by less than the noise floor at 1000, 3000 and 4000 points, and is worse at 500. GenZ-LIO: compared with its stock budget, ATE changes by less than the noise floor at 0.5×, 1.5× and 2× that budget, and is worse at 0.25×. lightning-lm, on ARC-6: the same pattern over the same factors. All three: ms_p95 grows roughly in proportion to the point budget. |
| **Falsified if** | In any system, a budget larger than the stock one improves ATE by more than the noise floor on every judged mission. That would mean the stock budget is too small. |
| **Decision rule** | Applied to each system separately. Adopt a smaller budget as that system's new default if its ATE is not worse than the stock budget's by more than the noise floor on any judged mission and it cuts ms_p95 by at least 10 %; if several qualify, the smallest is adopted. Keep the stock budget (reject) if no smaller budget qualifies. The result is inconclusive for a system if a larger budget improves ATE by more than the noise floor on at least two of the three dev missions (lightning-lm: on ARC-6); a follow-up experiment then chooses a new default. For lightning-lm only ARC-6 is judged. Verdict: adopt if every system adopts a smaller budget, reject if every system keeps its stock budget, and inconclusive otherwise. The summary at the top gives each system's result. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `n500` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: 500 points per scan (stock 2000) |
| `n1000` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: 1000 points per scan (stock 2000) |
| `n3000` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: 3000 points per scan (stock 2000) |
| `n4000` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: 4000 points per scan (stock 2000) |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_x0p25` | GenZ-LIO | `genz` | GenZ-LIO: 0.25 × the stock budget, 250 to 1000 points per scan (stock 1000 to 4000) |
| `genz_x0p5` | GenZ-LIO | `genz` | GenZ-LIO: 0.5 × the stock budget, 500 to 2000 points per scan (stock 1000 to 4000) |
| `genz_x1p5` | GenZ-LIO | `genz` | GenZ-LIO: 1.5 × the stock budget, 1500 to 6000 points per scan (stock 1000 to 4000) |
| `genz_x2` | GenZ-LIO | `genz` | GenZ-LIO: 2 × the stock budget, 2000 to 8000 points per scan (stock 1000 to 4000) |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_leaf_0p40` | lightning-lm | `lightning` | lightning-lm: scan voxel 0.4 m (stock 0.2 m), about 0.25 × the points |
| `lightning_leaf_0p28` | lightning-lm | `lightning` | lightning-lm: scan voxel 0.28 m (stock 0.2 m), about 0.5 × the points |
| `lightning_leaf_0p16` | lightning-lm | `lightning` | lightning-lm: scan voxel 0.16 m (stock 0.2 m), about 1.5 × the points |
| `lightning_leaf_0p14` | lightning-lm | `lightning` | lightning-lm: scan voxel 0.14 m (stock 0.2 m), about 2 × the points |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ms_mean`, `ms_p95`, `rss_mb`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-016`.
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
lvx run EXP-016 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-016                  # runs.csv + summary.json
lvx figures EXP-016
lvx viewer EXP-016                # on the host: map + trajectories for the 3D viewer
lvx report EXP-016
```
<!-- lvx:end reproduce -->
