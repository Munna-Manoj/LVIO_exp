# EXP-012 — Does skipping bad camera frames make the camera pay for itself?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P5 (Camera and backend) · **System:** `se3-lvio` · **Depends on:** EXP-004
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
| **`baseline` (S9b)** | SE(3)-LVIO's config `se3lvio_S9b`: two LiDARs (Hesai and Livox), the IMU and the front camera. |
| **S9a** | SE(3)-LVIO's config `se3lvio_S9a`: two LiDARs and the IMU, no camera. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | The frame check is added to its camera update. |
| GenZ-LIO | no | GenZ-LIO uses no camera. |
| lightning-lm | no | lightning-lm uses no camera. |

| | |
|---|---|
| **Question** | Does skipping SE(3)-LVIO's camera update on dark or low-texture frames improve ATE and scan time? |
| **Hypothesis** | Dark or featureless frames give camera residuals that pull the pose the wrong way. Skipping them keeps the useful frames and saves time. |
| **Prediction** | S9b with the frame check: ATE at most S9a's (no camera), and ms_p95 lower than S9b's. |
| **Falsified if** | ATE changes by less than the noise floor and ms_p95 does not drop. |
| **Decision rule** | Each system is run with and without the frame check (SE(3)-LVIO: `img_gate` with it, `baseline` without it). On each mission, the side with the frame check is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. The frame check helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. The frame check hurts a system if the side with it is worse on any mission. Verdict: adopt if the frame check helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S9b`, unchanged |
| `img_gate` | SE(3)-LVIO | `baseline` | SE(3)-LVIO S9b: skip the camera update if the mean brightness is below 25 or the image gradient energy is below its 10th percentile |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-012`.
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
lvx run EXP-012 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-012                  # runs.csv + summary.json
lvx figures EXP-012
lvx viewer EXP-012                # on the host: map + trajectories for the 3D viewer
lvx report EXP-012
```
<!-- lvx:end reproduce -->
