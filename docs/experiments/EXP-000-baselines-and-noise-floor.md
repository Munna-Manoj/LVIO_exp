# EXP-000 — How large is run-to-run noise, and do the pre-repo baselines reproduce?

**TL;DR:** adopt. All six stock configs reproduce their earlier ARC-6 ATE exactly, from SE(3)-LVIO S8 at 0.8055 cm to lightning-lm stock at 1.6391 cm. Every run keeps at least 99.87 % of the scans. In 16 of the 18 config–mission pairs, the five repeats are bit-for-bit identical, so the noise floor is the minimum (σ = 0.005 cm). The exception is S9c on EIG-2 and SNOW-3, where σ is 0.0013 and 0.0053 cm.

<!-- lvx:begin status -->
**Status:** ✅ concluded · verdict **🟢 adopt** · **Phase:** P0 (Foundation: baselines and noise floor) · **System:** `both` · **Depends on:** none
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
| **`s9a` (S9a)** | SE(3)-LVIO's config `se3lvio_S9a`: two LiDARs (Hesai and Livox) and the IMU. |
| **`s9b` (S9b)** | SE(3)-LVIO's config `se3lvio_S9b`: S9a plus the front camera. |
| **`s9c` (S9c)** | SE(3)-LVIO's full config `se3lvio_S9c`: S9b plus the online backend (plane bundle adjustment and iSAM2). |
| **`ll_stock`** | lightning-lm's config `lightning_stock`: upstream's settings, with only the GrandTour sensor calibration set. |
| **`ll_indoor`** | lightning-lm's config `lightning_indoor`: `ll_stock` with 0.2 m grids for indoor scale. |
| **earlier value** | The ARC-6 ATE of each config from runs made before this repository existed, recomputed with `lvx.evaluate` (each config's `reference_result`). |
| **pose_coverage** | The share of the scans in the IMU's time span for which the system produced a pose. 1.0 means one pose per scan. |
| **deterministic** | Identical runs give bit-for-bit identical trajectories (σ = 0). |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Its four configs S8, S9a, S9b and S9c. |
| lightning-lm | yes | Its stock and indoor configs. |
| GenZ-LIO | no | GenZ-LIO was added later; its noise floor comes from EXP-022 (EXP-021 is superseded). |

| | |
|---|---|
| **Question** | How much does ATE vary between identical runs of each baseline on the dev missions, and do the pre-repo ARC-6 numbers reproduce inside the harness? |
| **Hypothesis** | Multithreaded map updates (OpenMP) make runs non-deterministic; the spread is small but not zero, and it sets the smallest effect any later experiment may claim. |
| **Prediction** | σ(ATE) per baseline and mission below 0.05 cm. On ARC-6 every mean is within 3σ of the pre-repo number (S8 0.8055, S9a 0.8916, S9b 0.8976, S9c 0.8989, lightning stock 1.6391, indoor 1.4066 cm; recomputed with lvx.evaluate from the pre-repo estimates). EIG-2 and SNOW-3 have no pre-repo numbers; there EXP-000 measures σ and the baselines only. Every run has pose_coverage ≥ 0.99. |
| **Falsified if** | any baseline misses its pre-repo ARC-6 number by more than 3σ, or any run has pose_coverage below 0.99. Either means the harness changed the system (wrong config, frame, time offset or core budget). |
| **Decision rule** | pass (verdict adopt = the harness is trusted) if every baseline reproduces on ARC-6 within 3σ and every run has pose_coverage ≥ 0.99; otherwise reject and fix the harness before any other experiment runs. The σ per (baseline, mission) from this experiment is the noise floor for all later ones (ADR-0004). |

<sub>The five fields in this table were locked when the experiment was approved (pre-registered in `spec.lock`) and cannot change.</sub>

> **Erratum (2026-10-12):** prediction says “S9c 0.8989”; it should say “S9c 0.8998”. Source: the pre-repo run log on the reference host gives S9c ARC-6 ate_rmse_cm 0.8998005 (recomputed with lvx.evaluate on 2026-10-08); the digits were swapped when the number was copied, and EXP-000 measured 0.8998. The frozen text is kept as approved.
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `s9a` | SE(3)-LVIO | – | swap baseline config to S9a (adds Livox) |
| `s9b` | SE(3)-LVIO | – | swap baseline config to S9b (adds camera) |
| `s9c` | SE(3)-LVIO | – | swap baseline config to S9c (adds backend) |
| `ll_stock` | lightning-lm | – | swap baseline config to lightning-lm stock |
| `ll_indoor` | lightning-lm | – | swap baseline config to lightning-lm indoor grid |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 5 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_median_cm`, `ate_max_cm`, `ms_mean`, `ms_p95`, `rss_mb`, `pose_coverage`
- **Commits:** repo fb04f8769c · system 1325fed, 9bba0e4e06
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
Each cell shows `ate_rmse_cm` as the mean ± standard deviation over the repeats. Δ is the variant's mean minus the mean of the variant it is compared with, on the same mission. An effect counts only when |Δ| is larger than 2 × the run-to-run standard deviation σ of that system's stock config (σ from this experiment; never below 0.005 cm).

| Mission | Variant | ate_rmse_cm | Δ | Effect | ms p95 | runs ok / failed |
|---|---|---|---|---|---|---|
| arc-6 | `baseline` | 0.805 ± 0.000 |  |  | 36.1 | 5 / 0 |
| eig-2 | `baseline` | 2.489 ± 0.000 |  |  | 48.5 | 5 / 0 |
| snow-3 | `baseline` | 1.265 ± 0.000 |  |  | 50.3 | 5 / 0 |
| arc-6 | `s9a` | 0.892 ± 0.000 | +0.086 | ❔ no noise floor | 44.7 | 5 / 0 |
| eig-2 | `s9a` | 1.891 ± 0.000 | -0.598 | ❔ no noise floor | 63.1 | 5 / 0 |
| snow-3 | `s9a` | 1.362 ± 0.000 | +0.097 | ❔ no noise floor | 64.6 | 5 / 0 |
| arc-6 | `s9b` | 0.898 ± 0.000 | +0.092 | ❔ no noise floor | 67.3 | 5 / 0 |
| eig-2 | `s9b` | 2.081 ± 0.000 | -0.408 | ❔ no noise floor | 75.3 | 5 / 0 |
| snow-3 | `s9b` | 1.428 ± 0.000 | +0.163 | ❔ no noise floor | 78.1 | 5 / 0 |
| arc-6 | `s9c` | 0.900 ± 0.000 | +0.094 | ❔ no noise floor | 71.5 | 5 / 0 |
| eig-2 | `s9c` | 1.695 ± 0.001 | -0.795 | ❔ no noise floor | 111.7 | 5 / 0 |
| snow-3 | `s9c` | 1.364 ± 0.005 | +0.099 | ❔ no noise floor | 102.6 | 5 / 0 |
| arc-6 | `ll_stock` | 1.639 ± 0.000 | +0.834 | ❔ no noise floor | 32.2 | 5 / 0 |
| eig-2 | `ll_stock` | 464.587 ± 0.000 | +462.098 | ❔ no noise floor | 17.2 | 5 / 0 |
| snow-3 | `ll_stock` | 122.000 ± 0.000 | +120.735 | ❔ no noise floor | 19.7 | 5 / 0 |
| arc-6 | `ll_indoor` | 1.407 ± 0.000 | +0.601 | ❔ no noise floor | 35.8 | 5 / 0 |
| eig-2 | `ll_indoor` | 294.210 ± 0.000 | +291.720 | ❔ no noise floor | 58.4 | 5 / 0 |
| snow-3 | `ll_indoor` | 41.193 ± 0.000 | +39.928 | ❔ no noise floor | 67.9 | 5 / 0 |

![effect](../assets/experiments/EXP-000/effect.png)

![pareto](../assets/experiments/EXP-000/pareto.png)

![error_time](../assets/experiments/EXP-000/error_time.png)

![traj_top](../assets/experiments/EXP-000/traj_top.png)

### Maps

Map rebuilt from the baseline's repeat-1 estimate, all repeat-1 trajectories, in the GT frame (`lvx viewer`). Open a mission in the [interactive 3D viewer](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-000) to orbit, hide the ceiling and toggle trajectories. Data: [GrandTour](https://huggingface.co/datasets/leggedrobotics/grand_tour_dataset) (MIT; Frey, Tuna et al., [arXiv:2602.18164](https://arxiv.org/abs/2602.18164)).

[![arc-6: map and trajectories](../assets/experiments/EXP-000/viewer/arc-6_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-000&mission=arc-6)

[![eig-2: map and trajectories](../assets/experiments/EXP-000/viewer/eig-2_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-000&mission=eig-2)

[![snow-3: map and trajectories](../assets/experiments/EXP-000/viewer/snow-3_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-000&mission=snow-3)
<!-- lvx:end results -->

- **Identical runs give identical results.** In 16 of the 18 config–mission pairs, σ is 0.000 cm (Results table), and the five `estimate.tum` files have the same md5. Only `s9c` varies: on EIG-2 (σ 0.001 cm, 5 different estimates) and on SNOW-3 (σ 0.005 cm, 3 different estimates).
- **The earlier ARC-6 numbers reproduce exactly.** `baseline` 0.805, `s9a` 0.892, `s9b` 0.898, `s9c` 0.900, `ll_stock` 1.639 and `ll_indoor` 1.407 cm (Results table, ARC-6 rows). Each equals the earlier run's ATE to the 4 decimals that runs.csv keeps. The spec's S9c number had a typo; see Threats to validity.
- **lightning-lm loses track on the two field missions.** `ll_stock` reaches 464.6 cm on EIG-2 and 122.0 cm on SNOW-3; `ll_indoor` reaches 294.2 and 41.2 cm (Results table). The top view shows lightning-lm's trajectory bending away from the ground truth on EIG-2 (traj_top.png), although every lightning-lm run still produces a pose for at least 99.87 % of the scans.
- **SE(3)-LVIO stays between 0.8 and 2.5 cm on every mission.** Its other configs differ from S8 by −0.80 to +0.16 cm (Δ column). Those differences are far above the noise floor, but EXP-000 makes no claim about them; later experiments do.
- **More sensors cost more time and memory.** On ARC-6, ms_p95 grows from 36 ms (S8) to 45 (S9a), 67 (S9b) and 71 ms (S9c). The two configs with the camera use 4.1 to 8.4 GB of memory, against 0.25 to 1.1 GB for the others (pareto.png, `rss_mb` in summary.json).

## Discussion

The hypothesis expected SE(3)-LVIO's parallel map updates (OpenMP) to make identical runs differ. They do not. The input is replayed from files in the same order every time, and SE(3)-LVIO's parallel loops evidently combine their results in a fixed order; we have not traced how. Each run therefore computes the same floating-point numbers. As a result, S8, S9a, S9b and both lightning-lm configs are deterministic on 4 cores.

S9c is the only config with run-to-run noise, and it is also the only config with the backend (plane bundle adjustment and an iSAM2 pose graph). On ARC-6 its runs are identical; on the two longer field missions they differ slightly. A likely cause is the moment at which the frontend picks up the backend's results, which depends on thread timing. We have not traced which call is responsible. EXP-014 works on the backend and should confirm it.

What this means for later experiments ([ADR-0004](../process/decisions/ADR-0004-noise-floor-decision-rule.md)):
- With σ = 0, the minimum σ of 0.005 cm applies. On a deterministic config, any ATE change of more than 2 × 0.005 = 0.01 cm counts as an effect.
- That threshold is strict about the number but weak about its meaning. A deterministic system can move by 0.01 cm for a reason unrelated to the change, for example a different code path taken once.
- Later reports should therefore also say whether an effect is consistent across missions, not only whether it is above the noise floor.

lightning-lm's large errors on EIG-2 and SNOW-3 belong to lightning-lm's configs, not to the harness: the same harness reproduces lightning-lm exactly on ARC-6. Neither lightning-lm config was tuned for these missions, and glacier and snow-field scans offer few planes to match against. Whether a fair retune closes the gap is the question of EXP-019. Background on the residual model is in [docs/explain](../explain/README.md).

## Verdict

**Adopt: the harness is trusted.** The frozen rule asks for two things.
1. **Every config's ARC-6 ATE within 3σ of its earlier value.** All six ARC-6 means equal the earlier values, recomputed with `lvx.evaluate`. The gap is 0.0000 cm at 4 decimals; with the minimum σ, the 3σ band is at least 0.015 cm.
2. **Every run with pose_coverage ≥ 0.99.** The lowest pose_coverage of the 90 runs is 0.9987 (`ll_stock` and `ll_indoor` on SNOW-3).

The σ of each config on each mission (summary.json) is now the noise floor for every later experiment.

## Threats to validity

- **The spec's S9c number has a typo.** The prediction lists S9c as 0.8989 cm. The earlier run's log on the reference host says 0.8998005 cm, which is what EXP-000 measured. The typo is recorded as an erratum under the pre-registered fields (`lvx exp erratum`). The frozen text and `spec.lock` are unchanged, and `configs/baselines/se3lvio_S9c.yaml` now says 0.8998. Read literally, 0.8989 would still be inside the 3σ band (|0.8998 − 0.8989| = 0.0009 cm, below 3 × 0.005 cm), so the verdict does not depend on the typo.
- **Reproduction means the same code on the same host.** The earlier runs and EXP-000 both ran on the reference host with the same system commits. This shows the harness does not change the systems. It does not show that the numbers carry over to another machine or another number of cores; EXP-017 covers the core budget.
- **Three dev missions only.** Determinism and the noise floor were measured on ARC-6, EIG-2 and SNOW-3. A mission with more loop closures could make S9c's backend noisier than on SNOW-3.
- **lightning-lm's input was converted by us.** lightning-lm reads ROS 2 bags, which `offline_to_ros2bag.py` makes from the mission files. ARC-6 reproduces, so the conversion is right for ARC-6. A mission-specific conversion problem on EIG-2 or SNOW-3 (for example the IMU rate) would also inflate lightning-lm's error, and would look the same in this table.
- **pose_coverage slightly above 1.** `s9b` and `s9c` on SNOW-3 report 1.0004: 2319 estimated poses for 2318 scans in the IMU's time span. One extra pose at the start or the end does not affect the ≥ 0.99 rule. It does show that the camera configs do not produce exactly one pose per scan.

## Failures

None: 90 of 90 runs are `ok`, and none ran from uncommitted code (Results table).

One timing caveat concerns `baseline` on ARC-6, repeat r3, started at 11:11:47 on 2026-10-08. From about 11:12 to 11:13, a test of ours (`lvx viewer`, not limited to particular cores) ran on the same host. Because the runs are deterministic, every repeat does the same work on every scan. r3 can therefore be compared with the other four repeats scan by scan: each repeat against the per-scan median of the other four, from the runs' `timing.csv`.

| Repeat | ms_mean | ms_p95 | ms_max | Extra time per scan, whole run | Extra time per scan, last quarter |
|---|---|---|---|---|---|
| r1 | 27.41 | 36.48 | 54.4 | +0.70 ms | +0.25 ms |
| r2 | 26.94 | 33.21 | 55.8 | +0.15 ms | −0.07 ms |
| **r3** | 27.68 | 38.84 | 77.8 | +0.99 ms | **+2.65 ms** |
| r4 | 27.78 | 35.07 | 54.2 | +1.22 ms | +0.20 ms |
| r5 | 27.39 | 36.77 | 58.7 | +0.70 ms | +0.33 ms |

- Over the whole run, r3 is no slower than r4. The interference shows only in r3's last quarter (about 11:13:17 to 11:13:47), which is where r3's high ms_p95 and ms_max come from.
- r3's ATE is unaffected: its `estimate.tum` has the same md5 as the other repeats'.
- The run is kept. Runs are append-only, and rerunning to remove an inconvenient run is not allowed (CLAUDE.md law 5).
- Timing claims about this config and mission should use the median over the repeats: ms_mean 27.41 and ms_p95 36.48 (summary.json).
- Since this run, every other job on the host stays off cores 0 to 3.

## Reproduce

<!-- lvx:begin reproduce -->
```bash
lvx run EXP-000 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-000                  # runs.csv + summary.json
lvx figures EXP-000
lvx viewer EXP-000                # on the host: map + trajectories for the 3D viewer
lvx report EXP-000
```

What `lvx run` executed for each variant (repeat 1; all runs are in `results/manifests/`):

**baseline** (from `systems/se3-lvio`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim)):

```bash
DATA="$GRANDTOUR" CPUSET=0-3 IMAGE="$IMAGE" bash scripts/run_se3lio.sh arc-6 --tag EXP-000-baseline__arc-6__r1 --lio-only
```

**ll_indoor** (from `.`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim), `$LIGHTNING_WS` = the lightning-lm colcon workspace built by scripts/build_lightning.sh, `$BAG` = the mission as a ROS 2 bag: <run_root>/derived/lightning-bags/<mission>):

```bash
podman run --rm -v "$LIGHTNING_WS":/ws -v "$BAG":/bag:ro -v "$OUT":/out -w /ws/src/lightning-lm "$IMAGE" bash -c 'source /opt/ros/humble/setup.bash && source /ws/install/setup.bash && taskset -c 0-3 ./bin/run_lio_tum --input_bag /bag --config /out/config.yaml --output /out/arc-6_imu.tum --timing /out/timing.csv --log_dir /out' > "$OUT/run.log" 2>&1 && python3 systems/se3-lvio/tools/to_prism.py "$MISSION/comfort_offline/calib.json" "$OUT/arc-6_imu.tum" "$OUT/estimate.tum"
```

**ll_stock** (from `.`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim), `$LIGHTNING_WS` = the lightning-lm colcon workspace built by scripts/build_lightning.sh, `$BAG` = the mission as a ROS 2 bag: <run_root>/derived/lightning-bags/<mission>):

```bash
podman run --rm -v "$LIGHTNING_WS":/ws -v "$BAG":/bag:ro -v "$OUT":/out -w /ws/src/lightning-lm "$IMAGE" bash -c 'source /opt/ros/humble/setup.bash && source /ws/install/setup.bash && taskset -c 0-3 ./bin/run_lio_tum --input_bag /bag --config /out/config.yaml --output /out/arc-6_imu.tum --timing /out/timing.csv --log_dir /out' > "$OUT/run.log" 2>&1 && python3 systems/se3-lvio/tools/to_prism.py "$MISSION/comfort_offline/calib.json" "$OUT/arc-6_imu.tum" "$OUT/estimate.tum"
```

**s9a** (from `systems/se3-lvio`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim)):

```bash
DATA="$GRANDTOUR" CPUSET=0-3 IMAGE="$IMAGE" bash scripts/run_se3lio.sh arc-6 --tag EXP-000-s9a__arc-6__r1 --lio-only --lidar multi
```

**s9b** (from `systems/se3-lvio`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim)):

```bash
DATA="$GRANDTOUR" CPUSET=0-3 IMAGE="$IMAGE" bash scripts/run_se3lio.sh arc-6 --tag EXP-000-s9b__arc-6__r1 --lidar multi
```

**s9c** (from `systems/se3-lvio`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim)):

```bash
DATA="$GRANDTOUR" CPUSET=0-3 IMAGE="$IMAGE" bash scripts/run_se3lio.sh arc-6 --tag EXP-000-s9c__arc-6__r1 --lidar multi --backend
```
<!-- lvx:end reproduce -->
