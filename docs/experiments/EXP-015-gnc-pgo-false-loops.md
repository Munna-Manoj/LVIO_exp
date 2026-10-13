# EXP-015 — Does GNC protect the pose graph from false loops?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P6 (Stress tests) · **System:** `se3-lvio` · **Depends on:** EXP-014
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
| **`baseline` (S9c)** | SE(3)-LVIO's full config `se3lvio_S9c`: S9b plus the online backend (plane bundle adjustment and iSAM2). |
| **false loop** | A loop closure between two places that are not the same, added on purpose by the stress profile. |
| **GNC** | Graduated non-convexity: the solver starts by trusting every factor a little and gradually gives factors that disagree with the rest a weight of 0. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Huber and GNC kernels on its loop factors. |
| GenZ-LIO | no | GenZ-LIO has no backend. |
| lightning-lm | no | Not yet: this needs lightning-lm's loop closure running in our harness, which EXP-014 adds. A later experiment can add it. |

| | |
|---|---|
| **Question** | When 1 to 3 false loop closures are injected, does GNC (gtsam::GncOptimizer) keep ATE at the clean level where a Huber kernel does not? |
| **Hypothesis** | A single false loop can bend a pose graph. GNC-TLS is designed for exactly this case: the false factor starts far from its true value and has high leverage. |
| **Prediction** | With Huber, ATE grows with each injected loop. With GNC, ATE changes by less than the noise floor compared with the clean run. |
| **Falsified if** | With GNC, ATE is worse than the clean run by more than the noise floor after one injected loop. |
| **Decision rule** | Compare each variant with the clean run (no injected loops) on each dev mission. Adopt GNC if `gnc_pgo` is within the noise floor of the clean run on every mission while `huber_pgo` is worse by more than the noise floor on at least one. Reject GNC if `gnc_pgo` is also worse by more than the noise floor on any mission. Otherwise inconclusive. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S9c`, unchanged |
| `huber_pgo` | SE(3)-LVIO | `baseline` | SE(3)-LVIO S9c: loop factors with a Huber kernel |
| `gnc_pgo` | SE(3)-LVIO | `baseline` | SE(3)-LVIO S9c: loop factors solved with GncOptimizer (TLS) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`
- **Stress profile:** `false-loops-3`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-015`.
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
lvx run EXP-015 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-015                  # runs.csv + summary.json
lvx figures EXP-015
lvx viewer EXP-015                # on the host: map + trajectories for the 3D viewer
lvx report EXP-015
```
<!-- lvx:end reproduce -->
