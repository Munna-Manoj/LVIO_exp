# EXP-003 — Does gradually rejecting outliers across the update iterations help?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P1 (Outliers and robustness) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-002
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
| **GNC-TLS** | Graduated non-convexity with a truncated least-squares cost. Each residual gets a weight between 0 and 1. The parameter μ starts small, which accepts almost every point, and grows by × 1.4 per iteration until large residuals get weight 0. |
| **iteration** | One pass of the scan update. Each scan is re-matched and re-solved up to 4 times in all three stock configs. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | GNC-TLS with 4 and with 8 iterations. |
| GenZ-LIO | yes | GNC-TLS with 4 and with 8 iterations. |
| lightning-lm | yes | GNC-TLS with 4 and with 8 iterations. |

| | |
|---|---|
| **Question** | Does GNC-TLS weighting, which starts permissive and becomes strict over the update iterations, improve ATE compared with each system's stock weighting? |
| **Hypothesis** | In the first iteration the pose is still off, so a strict rule rejects good points. GNC-TLS starts with a wide acceptance and narrows it as the pose improves. With only 4 iterations per scan, the schedule may not finish. |
| **Prediction** | All three systems: GNC-TLS with the stock iteration count changes ATE by less than the noise floor. GNC-TLS with 8 iterations improves ATE on ARC-6 and costs more scan time. |
| **Falsified if** | GNC-TLS with 8 iterations is not better than the stock config on ARC-6 in any system. |
| **Decision rule** | Each system is run with and without GNC-TLS weighting (SE(3)-LVIO: `gnc_tls or gnc_tls_8it` with it, `baseline` without it; GenZ-LIO: `genz_gnc_tls or genz_gnc_tls_8it` with it, `genz` without it; lightning-lm: `lightning_gnc_tls or lightning_gnc_tls_8it` with it, `lightning` without it). On each mission, the side with GNC-TLS weighting is better if its ATE is lower by more than the noise floor, and worse if its ATE is higher by more than the noise floor. GNC-TLS weighting helps a system if the side with it is better on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. GNC-TLS weighting hurts a system if the side with it is worse on any mission. For lightning-lm only ARC-6 is judged: GNC-TLS weighting helps lightning-lm if the side with it is better on ARC-6 with less than 10 % more ms_p95, and hurts lightning-lm if it is worse on ARC-6. Verdict: adopt if GNC-TLS weighting helps every system that takes part, reject if it hurts every one, and inconclusive otherwise. The summary at the top of the page gives the result for each system. A system's better variant (lower mean ATE) stands for that system. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `gnc_tls` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: GNC-TLS weights, μ × 1.4 per iteration |
| `gnc_tls_8it` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: GNC-TLS weights with 8 iterations, so that the schedule finishes |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_gnc_tls` | GenZ-LIO | `genz` | GenZ-LIO: GNC-TLS weights, μ × 1.4 per iteration |
| `genz_gnc_tls_8it` | GenZ-LIO | `genz` | GenZ-LIO: GNC-TLS weights with 8 iterations |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_gnc_tls` | lightning-lm | `lightning` | lightning-lm: GNC-TLS weights, μ × 1.4 per iteration |
| `lightning_gnc_tls_8it` | lightning-lm | `lightning` | lightning-lm: GNC-TLS weights with 8 iterations |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-003`.
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
lvx run EXP-003 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-003                  # runs.csv + summary.json
lvx figures EXP-003
lvx viewer EXP-003                # on the host: map + trajectories for the 3D viewer
lvx report EXP-003
```
<!-- lvx:end reproduce -->
