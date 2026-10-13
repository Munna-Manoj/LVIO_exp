# EXP-013 — Does brightness compensation help the camera update?

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
| SE(3)-LVIO | yes | Brightness compensation is added to its camera update. |
| GenZ-LIO | no | GenZ-LIO uses no camera. |
| lightning-lm | no | lightning-lm uses no camera. |

| | |
|---|---|
| **Question** | Does estimating a per-frame brightness gain and offset (a, b) improve S9b's ATE when the lighting changes? |
| **Hypothesis** | The camera update assumes a patch keeps its brightness between frames. Smoke and changing light break that assumption. FAST-LIVO2 estimates the exposure for this reason. |
| **Prediction** | Better than S9b on missions with lighting changes; ATE changes by less than the noise floor elsewhere. |
| **Falsified if** | ATE changes by less than the noise floor on every dev mission. |
| **Decision rule** | Each system is run with and without brightness compensation (SE(3)-LVIO: `affine_ab` with it, `baseline` without it). On each mission, the side with brightness compensation is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. Brightness compensation helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. Brightness compensation hurts a system if the side with it is worse on any mission. Verdict: adopt if brightness compensation helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S9b`, unchanged |
| `affine_ab` | SE(3)-LVIO | `baseline` | SE(3)-LVIO S9b: per-frame brightness gain and offset (a, b) in the camera residual |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-013`.
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
lvx run EXP-013 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-013                  # runs.csv + summary.json
lvx figures EXP-013
lvx viewer EXP-013                # on the host: map + trajectories for the 3D viewer
lvx report EXP-013
```
<!-- lvx:end reproduce -->
