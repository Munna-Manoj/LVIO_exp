# EXP-017 — Do all three systems hold 10 Hz and 20 Hz on four cores?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P7 (Embedded real time) · **System:** `se3-lvio` + `lightning-lm` + `genz-lio` · **Depends on:** EXP-016
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
| **S9b** | SE(3)-LVIO's config `se3lvio_S9b`: two LiDARs (Hesai and Livox), the IMU and the front camera. |
| **4 pinned cores** | Each run is limited to the same 4 CPU cores (cores 0 to 3 of the reference host) with taskset. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | S8 and S9b. |
| GenZ-LIO | yes | Its stock config. |
| lightning-lm | yes | Its indoor config. |

| | |
|---|---|
| **Question** | With 4 pinned cores, what are the scan times (ms_p95 and maximum) of SE(3)-LVIO (S8 and S9b), lightning-lm and GenZ-LIO? |
| **Hypothesis** | All three fit 10 Hz (100 ms per scan) on 4 server cores. lightning-lm has the most headroom for 20 Hz (50 ms per scan). Raspberry Pi 5 cores are about 2 to 3 times slower, so the margin on the server must be large. |
| **Prediction** | S8 ms_p95 below 50 ms; S9b above 50 ms; lightning-lm below 30 ms on ARC-6; GenZ-LIO below 100 ms on every dev mission but above 50 ms on EIG-2 and SNOW-3 (EXP-022 measured 38, 66 and 61 ms). |
| **Falsified if** | S8's ms_p95 is above 100 ms on 4 cores: SE(3)-LVIO would not run in real time even on server cores. |
| **Decision rule** | Report only. The verdict is inconclusive, unless a system's ms_p95 is above 100 ms on a dev mission; that system is then rejected for 10 Hz on this host. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `s9b` | SE(3)-LVIO | – | SE(3)-LVIO's config S9b (two LiDARs, IMU and camera) |
| `lightning` | lightning-lm | – | lightning-lm's indoor config |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ms_p95`, secondary `ms_mean`, `ms_max`, `rss_mb`, `ate_rmse_cm`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-017`.
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
lvx run EXP-017 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-017                  # runs.csv + summary.json
lvx figures EXP-017
lvx viewer EXP-017                # on the host: map + trajectories for the 3D viewer
lvx report EXP-017
```
<!-- lvx:end reproduce -->
