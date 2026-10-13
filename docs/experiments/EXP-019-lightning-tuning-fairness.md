# EXP-019 — Is lightning-lm tuned fairly?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** PX (Cross-system comparison) · **System:** `lightning-lm` · **Depends on:** EXP-000
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
| **lightning-lm on the field missions** | Both lightning-lm configs lose track on EIG-2 and SNOW-3 in EXP-000 (`lightning`: 294 cm and 41 cm). A lightning-lm variant is therefore judged on ARC-6 only. Its EIG-2 and SNOW-3 numbers are still reported. |
| **`baseline` (lightning)** | lightning-lm's config `lightning_indoor`: upstream's settings with 0.2 m grids. |
| **iVox grid** | The cell size of lightning-lm's hashed voxel map, used to find a point's 5 nearest map points. |
| **plane_icp_weight** | A factor on the weight of all point-to-plane residuals in lightning-lm's scan update. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | no | SE(3)-LVIO's stock config was tuned by its authors on these sensors; it is the comparison point. |
| GenZ-LIO | no | GenZ-LIO's tuning fairness is EXP-026. |
| lightning-lm | yes | Three config changes, one at a time. |

| | |
|---|---|
| **Question** | With the same tuning budget on the dev missions that SE(3)-LVIO had, how close does lightning-lm get to SE(3)-LVIO? |
| **Hypothesis** | Most of the ARC-6 gap between lightning-lm (1.41 cm) and SE(3)-LVIO S8 (0.81 cm) comes from the map and the residual weights, not from tuning. Tuning closes at most a third of the gap. |
| **Prediction** | The best tuned variant is within 0.3 cm of lightning-lm's indoor config on ARC-6. |
| **Falsified if** | A tuned lightning-lm matches SE(3)-LVIO S8's ARC-6 ATE within the noise floor. |
| **Decision rule** | Only ARC-6 is judged. Adopt the tuned variant with the lowest ARC-6 ATE as lightning-lm's tuned config if it is better than the indoor config by more than the noise floor with less than 10 % more ms_p95. Reject (the indoor config stays) if every variant is worse on ARC-6. Otherwise inconclusive. A variant that brings EIG-2 or SNOW-3 below 10 cm is reported as a finding. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | lightning-lm | – | the stock config `lightning_indoor`, unchanged |
| `grid_0p1` | lightning-lm | `baseline` | lightning-lm: iVox grid 0.1 m (indoor config 0.2 m) |
| `icp_w_1000` | lightning-lm | `baseline` | lightning-lm: plane_icp_weight 1000 (indoor config 300) |
| `filter_1` | lightning-lm | `baseline` | lightning-lm: keep every point before downsampling (point_filter_num 1, indoor config 2) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-019`.
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
lvx run EXP-019 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-019                  # runs.csv + summary.json
lvx figures EXP-019
lvx viewer EXP-019                # on the host: map + trajectories for the 3D viewer
lvx report EXP-019
```
<!-- lvx:end reproduce -->
