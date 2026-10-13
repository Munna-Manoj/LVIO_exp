# EXP-002 — Does a robust kernel in the scan update beat a hard limit alone?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P1 (Outliers and robustness) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-001
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
| **robust kernel** | A weight that shrinks as a residual grows. Huber keeps full weight up to k and then falls as k / |r|. Cauchy falls smoothly as 1 / (1 + (r / c)²). |
| **residual (r)** | The distance between a scan point and its matched plane (or point) in the map. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Huber and Cauchy weights, scaled by each point's σ. |
| GenZ-LIO | yes | Huber and Cauchy weights, scaled by each point's σ. |
| lightning-lm | yes | Huber and Cauchy weights, scaled by the scan's robust residual spread. |

| | |
|---|---|
| **Question** | Does down-weighting points with large residuals (a robust kernel) improve ATE compared with a hard limit alone? |
| **Hypothesis** | The hard limit treats a point just inside it like a perfect match. A robust kernel gives such a point a smaller weight, so smoke and clutter that pass the limit pull the pose less. |
| **Prediction** | SE(3)-LVIO: Huber and Cauchy weights change ATE by less than the noise floor on EIG-2 and SNOW-3, and improve ATE on ARC-6 (smoke). GenZ-LIO: ATE changes by less than the noise floor, because GenZ-LIO already has two limits (point-to-plane and point-to-point). lightning-lm, on ARC-6: better, because lightning-lm gives every residual the same weight 1.0. |
| **Falsified if** | A kernel is worse than its system's stock config by more than the noise floor on ARC-6. |
| **Decision rule** | Each system is run with and without a robust kernel (SE(3)-LVIO: `huber or cauchy` with it, `baseline` without it; GenZ-LIO: `genz_huber or genz_cauchy` with it, `genz` without it; lightning-lm: `lightning_huber or lightning_cauchy` with it, `lightning` without it). On each mission, the side with a robust kernel is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. A robust kernel helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. A robust kernel hurts a system if the side with it is worse on any mission. For lightning-lm only ARC-6 is judged: a robust kernel helps lightning-lm if the side with it is better on ARC-6 with less than 10 % more ms_p95, and hurts lightning-lm if it is worse on ARC-6. Verdict: adopt if a robust kernel helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. A system's better kernel (lower mean ATE) stands for that system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `huber` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: Huber weight, k = 1.345σ |
| `cauchy` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: Cauchy weight, c = 2.385σ |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_huber` | GenZ-LIO | `genz` | GenZ-LIO: Huber weight, k = 1.345σ |
| `genz_cauchy` | GenZ-LIO | `genz` | GenZ-LIO: Cauchy weight, c = 2.385σ |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_huber` | lightning-lm | `lightning` | lightning-lm: Huber weight, k = 1.345 s |
| `lightning_cauchy` | lightning-lm | `lightning` | lightning-lm: Cauchy weight, c = 2.385 s |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-002`.
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
lvx run EXP-002 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-002                  # runs.csv + summary.json
lvx figures EXP-002
lvx viewer EXP-002                # on the host: map + trajectories for the 3D viewer
lvx report EXP-002
```
<!-- lvx:end reproduce -->
