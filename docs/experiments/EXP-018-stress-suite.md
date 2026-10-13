# EXP-018 — Which design choices matter when the data gets worse?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P6 (Stress tests) · **System:** `se3-lvio` + `lightning-lm` + `genz-lio` · **Depends on:** EXP-000
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
| **stress profile** | A controlled damage applied to the data before a run (configs/stress.yaml, suite-v1). |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | S8 under every profile. |
| GenZ-LIO | yes | Its stock config under every profile. |
| lightning-lm | yes | Its indoor config under every profile. |

| | |
|---|---|
| **Question** | Under controlled damage to the data (no Livox, 10 to 30 % of the scans dropped, 4 × fewer points per scan, the IMU shifted by ±5 ms), how much does each system's ATE get worse? |
| **Hypothesis** | SE(3)-LVIO is tuned for clean data and loses more when scans are dropped. lightning-lm's safeguards (EXP-006) make it lose less. GenZ-LIO's adaptive point budget makes it lose less when the points are thinned. |
| **Prediction** | Relative to its own clean ATE, lightning-lm loses less than SE(3)-LVIO when scans are dropped, and GenZ-LIO loses less than SE(3)-LVIO under 4 × thinning. SE(3)-LVIO stays the most accurate in absolute terms. The no-Livox profile does not change S8, GenZ-LIO or lightning-lm, which use the Hesai only. |
| **Falsified if** | SE(3)-LVIO loses the least, in relative terms, under every profile. |
| **Decision rule** | Report only. The verdict is inconclusive, with a table of how much each system loses under each profile. The table feeds the choice of safeguards in phase P2. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `lightning` | lightning-lm | – | lightning-lm's indoor config |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Stress profile:** `suite-v1`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-018`.
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
lvx run EXP-018 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-018                  # runs.csv + summary.json
lvx figures EXP-018
lvx viewer EXP-018                # on the host: map + trajectories for the 3D viewer
lvx report EXP-018
```
<!-- lvx:end reproduce -->
