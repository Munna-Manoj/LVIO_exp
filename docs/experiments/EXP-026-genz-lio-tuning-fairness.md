# EXP-026 — Is GenZ-LIO tuned fairly?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** PX (Cross-system comparison) · **System:** `genz-lio` · **Depends on:** EXP-022
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
| **`baseline` (genz_stock)** | GenZ-LIO's stock config: upstream's Hesai settings, with only the sensor calibration and the 4-core limit set. |
| **λ_po** | GenZ-LIO's weight factor for point-to-point residuals against point-to-plane ones; upstream calls it its most sensitive parameter. |
| **root voxel** | The size of the largest cube in GenZ-LIO's octree map. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | no | SE(3)-LVIO's stock config was tuned by its authors on these sensors; it is the comparison point. |
| GenZ-LIO | yes | Three config changes, one at a time. |
| lightning-lm | no | lightning-lm's tuning fairness is EXP-019. |

| | |
|---|---|
| **Question** | With the same tuning budget on the dev missions that SE(3)-LVIO had, how close does GenZ-LIO get to SE(3)-LVIO? |
| **Hypothesis** | Most of the SNOW-3 gap between GenZ-LIO (5.60 cm, EXP-022) and SE(3)-LVIO S8 (1.26 cm, EXP-000) comes from the state and the map design, not from tuning. Tuning closes at most a third of the gap. |
| **Prediction** | No variant brings GenZ-LIO's SNOW-3 ATE below 4.2 cm (a third of the gap closed). The best variant is within 0.3 cm of GenZ-LIO's stock config on ARC-6. |
| **Falsified if** | A tuned GenZ-LIO matches SE(3)-LVIO S8's SNOW-3 ATE within the noise floor. |
| **Decision rule** | Adopt the variant with the lowest mean ATE as GenZ-LIO's tuned config if it is better than the stock config by more than the noise floor on at least two dev missions, worse on none, with less than 10 % more ms_p95. Reject (the stock config stays) if every variant is worse on at least one dev mission. Otherwise inconclusive. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | GenZ-LIO | – | the stock config `genz_stock`, unchanged |
| `lambda_po_0p02` | GenZ-LIO | `baseline` | GenZ-LIO: λ_po 0.02 (stock 0.05) |
| `lambda_po_0p2` | GenZ-LIO | `baseline` | GenZ-LIO: λ_po 0.2 (stock 0.05) |
| `voxel_0p5` | GenZ-LIO | `baseline` | GenZ-LIO: root voxel 0.5 m (stock 1.0 m) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-026`.
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
lvx run EXP-026 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-026                  # runs.csv + summary.json
lvx figures EXP-026
lvx viewer EXP-026                # on the host: map + trajectories for the 3D viewer
lvx report EXP-026
```
<!-- lvx:end reproduce -->
