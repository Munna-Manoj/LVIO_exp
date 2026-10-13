# EXP-025 — Does thinning GenZ-LIO's point-to-point candidates cost accuracy?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `genz-lio` · **Depends on:** EXP-022
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
| **candidate** | A map point kept in a voxel so that GenZ-LIO's point-to-point residual can find a scan point's nearest map point. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | no | SE(3)-LVIO has no point-to-point candidates. If EXP-024 adopts point-to-point residuals for SE(3)-LVIO, a later experiment adds this question. |
| GenZ-LIO | yes | Its candidate count and its thinning ratio are varied. |
| lightning-lm | no | lightning-lm finds point-to-point matches through iVox's nearest-point search, not through a candidate pool. |

| | |
|---|---|
| **Question** | GenZ-LIO keeps up to 128 candidate points per map voxel for its point-to-point search, and divides that number by 4 each time a voxel is split. Does keeping more or fewer candidates change ATE, or only scan time? |
| **Hypothesis** | The nearest candidate is almost always among those kept, so the thinning saves time without losing matches. Keeping far fewer starts to miss the nearest match. |
| **Prediction** | No thinning (divide by 1) and 512 candidates: ATE changes by less than the noise floor, and ms_p95 is higher. 32 candidates: worse on EIG-2 and SNOW-3, where the point-to-point residual carries more of the update. |
| **Falsified if** | No thinning or 512 candidates improves ATE by more than the noise floor on at least two dev missions. That would mean the stock setting loses matches. |
| **Decision rule** | Compare each variant with `baseline` (GenZ-LIO's stock config). Adopt a variant that costs less ms_p95 than the stock setting if its ATE is not worse by more than the noise floor on any dev mission. Adopt a variant that costs more ms_p95 only if its ATE is better by more than the noise floor on at least two dev missions and worse on none. Reject (the stock setting stays) if no variant qualifies and at least one is worse by more than the noise floor; otherwise inconclusive. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | GenZ-LIO | – | the stock config `genz_stock`, unchanged |
| `ratio_1` | GenZ-LIO | `baseline` | GenZ-LIO: no thinning when a voxel is split (divide by 1; stock 4) |
| `cand_32` | GenZ-LIO | `baseline` | GenZ-LIO: 32 candidates per voxel (stock 128) |
| `cand_512` | GenZ-LIO | `baseline` | GenZ-LIO: 512 candidates per voxel (stock 128) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_mean`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-025`.
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
lvx run EXP-025 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-025                  # runs.csv + summary.json
lvx figures EXP-025
lvx viewer EXP-025                # on the host: map + trajectories for the 3D viewer
lvx report EXP-025
```
<!-- lvx:end reproduce -->
