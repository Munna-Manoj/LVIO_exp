# EXP-024 — Should points without a plane get a point-to-point residual?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-000, EXP-022
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
| **point-to-plane residual** | The distance from a scan point to its matched plane in the map. |
| **point-to-point residual** | The distance from a scan point to its nearest point in the map. GenZ-LIO uses it only for points that match no plane, weighted by λ_po. lightning-lm uses it for every point with at least 3 map neighbours, dropping residuals above 0.5 m, with a fixed weight of 100. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Point-to-point residuals are added for points without a plane. |
| GenZ-LIO | yes | GenZ-LIO has them; its variant switches them off. |
| lightning-lm | yes | lightning-lm has its own version (for every point); its variant switches it off. |

| | |
|---|---|
| **Question** | GenZ-LIO gives a point that matches no plane a point-to-point residual instead of dropping it. Does a point-to-point residual improve ATE, in each system? |
| **Hypothesis** | In open scenes many points fall where the map has no plane. Those points carry information that a point-to-plane update throws away. In confined scenes almost every point has a plane, so the extra residual rarely applies. |
| **Prediction** | SE(3)-LVIO with it: ATE changes by less than the noise floor on ARC-6, and is better on EIG-2 and SNOW-3. GenZ-LIO without it: ATE changes by less than the noise floor on ARC-6, and is worse on EIG-2 and SNOW-3. lightning-lm without its point-to-point residual, on ARC-6: ATE changes by less than the noise floor. |
| **Falsified if** | In neither SE(3)-LVIO nor GenZ-LIO is the side with point-to-point residuals better on EIG-2 or SNOW-3. |
| **Decision rule** | Each system is run with and without point-to-point residuals (SE(3)-LVIO: `p2p_fallback` with it, `baseline` without it; GenZ-LIO: `genz` with it, `genz_no_hybrid` without it; lightning-lm: `lightning` with it, `lightning_no_icp` without it). On each mission, the side with point-to-point residuals is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. Point-to-point residuals helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. Point-to-point residuals hurts a system if the side with it is worse on any mission. For lightning-lm only ARC-6 is judged: point-to-point residuals helps lightning-lm if the side with it is better on ARC-6 with less than 10 % more ms_p95, and hurts lightning-lm if it is worse on ARC-6. Verdict: adopt if point-to-point residuals helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `p2p_fallback` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: point-to-point residuals for points without a plane, weight factor λ_po 0.05 |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_no_hybrid` | GenZ-LIO | `genz` | GenZ-LIO: point-to-plane residuals only |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_no_icp` | lightning-lm | `lightning` | lightning-lm: point-to-plane residuals only |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `inliers_mean`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-024`.
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
lvx run EXP-024 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-024                  # runs.csv + summary.json
lvx figures EXP-024
lvx viewer EXP-024                # on the host: map + trajectories for the 3D viewer
lvx report EXP-024
```
<!-- lvx:end reproduce -->
