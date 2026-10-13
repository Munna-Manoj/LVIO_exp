# EXP-022 — How large is GenZ-LIO's run-to-run noise, with the protocol's IMU time offset?

**TL;DR:** adopt. With each mission's IMU time offset applied, all 15 GenZ-LIO runs are `ok`, and the five repeats of each mission are bit-for-bit identical (σ = 0), so GenZ-LIO's noise floor is the minimum (σ = 0.005 cm). Every run keeps at least 99.91 % of the scans. GenZ-LIO's ATE is 1.501 cm on ARC-6 (the limit was 3 cm), 2.341 cm on EIG-2 and 5.602 cm on SNOW-3. These numbers replace [EXP-021](EXP-021-genz-lio-baseline-and-noise-floor.md)'s, which were measured without the offset.

<!-- lvx:begin status -->
**Status:** ✅ concluded · verdict **🟢 adopt** · **Phase:** P0 (Foundation: baselines and noise floor) · **System:** `genz-lio` · **Depends on:** EXP-000
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
| **IMU time offset** | The delay between the IMU clock and the LiDAR clock, fitted once per mission (configs/missions.yaml `imu_dt`). The protocol applies it to every system. |
| **pose_coverage** | The share of the scans in the IMU's time span for which the system produced a pose. 1.0 means one pose per scan. |
| **deterministic** | Identical runs give bit-for-bit identical trajectories (σ = 0). |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| GenZ-LIO | yes | Its stock config, 5 repeats per mission. |
| SE(3)-LVIO | no | Its noise floor comes from EXP-000; its numbers are quoted for comparison. |
| lightning-lm | no | Its noise floor comes from EXP-000; its numbers are quoted for comparison. |

| | |
|---|---|
| **Question** | How much does ATE vary between identical runs of GenZ-LIO stock on the dev missions, and does the harness run it without dropping scans or mis-placing the LiDAR? |
| **Hypothesis** | GenZ-LIO's worker threads (correspondence search and map updates, runtime.max_threads 4) combine their results in a fixed order on an offline replay, as SE(3)-LVIO's frontend does (EXP-000), so its runs are deterministic or nearly so. With upstream's Hesai template and the GrandTour extrinsic it tracks every dev mission at centimetre level. |
| **Prediction** | σ(ATE) per mission below 0.05 cm. Every run has pose_coverage ≥ 0.99. ATE on ARC-6 below 3 cm. EXP-021 ran the same config without the IMU offset and got 1.382 (arc-6), 2.506 (eig-2) and 5.884 cm (snow-3); with the offset we expect each within ±20 % of those, since the offset is 5-6.5 ms and the IMU prior is only one input to each scan's update. |
| **Falsified if** | any run has pose_coverage below 0.99, any run fails, or ARC-6 ATE is 3 cm or more. Each means the harness or the config is wrong for GenZ-LIO (frame, extrinsic, timestamps, or core budget). |
| **Decision rule** | pass (verdict adopt = GenZ-LIO runs correctly in the harness, under the full protocol) if all 15 runs are ok with pose_coverage ≥ 0.99 and the ARC-6 mean ATE is below 3 cm; otherwise reject and fix the runner or config before any experiment uses GenZ-LIO. The σ per mission from this experiment is GenZ-LIO's noise floor for all later experiments (ADR-0004, ADR-0012). |

<sub>The five fields in this table were locked when the experiment was approved (pre-registered in `spec.lock`) and cannot change.</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | GenZ-LIO | – | the stock config `genz_stock`, unchanged |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 5 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_median_cm`, `ate_max_cm`, `ms_mean`, `ms_p95`, `rss_mb`, `pose_coverage`
- **Commits:** repo 3417882e7c · system 0936d34b61
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
Each cell shows `ate_rmse_cm` as the mean ± standard deviation over the repeats. Δ is the variant's mean minus the mean of the variant it is compared with, on the same mission. An effect counts only when |Δ| is larger than 2 × the run-to-run standard deviation σ of that system's stock config (σ from this experiment; never below 0.005 cm).

| Mission | Variant | ate_rmse_cm | Δ | Effect | ms p95 | runs ok / failed |
|---|---|---|---|---|---|---|
| arc-6 | `baseline` | 1.501 ± 0.000 |  |  | 38.2 | 5 / 0 |
| eig-2 | `baseline` | 2.341 ± 0.000 |  |  | 65.7 | 5 / 0 |
| snow-3 | `baseline` | 5.602 ± 0.000 |  |  | 61.4 | 5 / 0 |

![pareto](../assets/experiments/EXP-022/pareto.png)

### Maps

Map rebuilt from the baseline's repeat-1 estimate, all repeat-1 trajectories, in the GT frame (`lvx viewer`). Open a mission in the [interactive 3D viewer](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-022) to orbit, hide the ceiling and toggle trajectories. Data: [GrandTour](https://huggingface.co/datasets/leggedrobotics/grand_tour_dataset) (MIT; Frey, Tuna et al., [arXiv:2602.18164](https://arxiv.org/abs/2602.18164)).

[![arc-6: map and trajectories](../assets/experiments/EXP-022/viewer/arc-6_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-022&mission=arc-6)

[![eig-2: map and trajectories](../assets/experiments/EXP-022/viewer/eig-2_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-022&mission=eig-2)

[![snow-3: map and trajectories](../assets/experiments/EXP-022/viewer/snow-3_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-022&mission=snow-3)
<!-- lvx:end results -->

- **Identical runs give identical results.** σ is 0.000 cm on all three missions (Results table), and the five `estimate.tum` files of each mission have the same md5.
- **ARC-6 is at 1.501 cm, inside the pre-registered 3 cm limit.** For comparison, on the same mission EXP-000 measured SE(3)-LVIO S8 at 0.805 cm and lightning-lm at 1.407 cm (indoor config) and 1.639 cm (stock config).
- **The offset changes each mission's ATE by less than 9 %, in both directions.** Against EXP-021 (the same config without the offset):

  | Mission | EXP-021, no offset | EXP-022, with offset | Change |
  |---|---|---|---|
  | ARC-6 | 1.382 cm | 1.501 cm | +8.6 % (worse) |
  | EIG-2 | 2.506 cm | 2.341 cm | −6.6 % (better) |
  | SNOW-3 | 5.884 cm | 5.602 cm | −4.8 % (better) |

  All three are inside the ±20 % band that the prediction expected.
- **Coverage.** The lowest pose_coverage is 0.9991 (EIG-2). As in EXP-021, each run skips exactly one scan at the start, before GenZ-LIO's filter has initialised (the runner's `summary.json`: `skipped: 1`). The number of poses is also unchanged (3489 on ARC-6).
- **Cost on 4 cores.** ms_p95 is 38.2 ms on ARC-6, 65.7 ms on EIG-2 and 61.4 ms on SNOW-3; ms_mean is 32.2, 46.2 and 51.9 ms; memory is 0.49, 2.5 and 1.4 GB (pareto.png, `runs.csv`). These are within 8 % of EXP-021's timings. That is expected: the offset changes when the IMU samples fall, not how much work each scan takes.

## Discussion

GenZ-LIO is deterministic for the same reason as SE(3)-LVIO in EXP-000. The input is replayed from files in the same order every time, and GenZ-LIO's 4 worker threads evidently combine their results in a fixed order. GenZ-LIO's variants are therefore judged against the minimum noise floor: an ATE change of more than 0.01 cm counts as an effect (ADR-0004, ADR-0012). Later reports should also say whether an effect is consistent across missions.

The IMU time offset shifts every IMU timestamp by 4.8 to 6.5 ms against the LiDAR (configs/missions.yaml). That changes which IMU samples GenZ-LIO uses to predict each scan's motion and to correct the scan's distortion from that motion. The scan-to-map update then removes most of the prediction error, which is why ATE changes by millimetres and not centimetres.

The direction of the change is not consistent: ARC-6 got worse, while EIG-2 and SNOW-3 got better. So the offset is not "right" for GenZ-LIO on every mission. It is the protocol, applied the same way to every system (CLAUDE.md §3), and that is what makes GenZ-LIO's numbers comparable with EXP-000's.

The gap to SE(3)-LVIO S8 on SNOW-3 (5.602 against 1.265 cm, 4.4 ×) remains a question for the ablations, for example EXP-009 for the pose update and EXP-026 for tuning. Background: [SE(3) vs SO(3)×R³](../explain/se3-vs-so3xr3.md).

## Verdict

**Adopt: GenZ-LIO runs correctly in the harness, under the full protocol.** The frozen rule asks for all 15 runs `ok`, with pose_coverage ≥ 0.99, and an ARC-6 mean ATE below 3 cm. All 15 runs are `ok`, the lowest pose_coverage is 0.9991, and ARC-6 is 1.501 cm.

GenZ-LIO's σ is 0 on every mission, so its noise floor is the minimum. `lvx eval` takes it from EXP-022 for every variant that runs `genz_stock` (`noise_floor` in summary.json). EXP-021's noise floor is not used.

## Threats to validity

- **The limits were informed by earlier runs.** The 3 cm limit and the ±20 % band were set from EXP-021's numbers, and the spec says so. The pass is not in doubt (ARC-6 is at half the limit), but it is not a blind prediction.
- **Stock, not tuned.** `genz_stock` is upstream's Hesai config with only the sensor calibration and the 4-core limit set. Tuning on the dev missions may narrow the SNOW-3 gap. That is a fairness experiment (EXP-026, like EXP-019 for lightning-lm), not this one.
- **Our runner, not upstream's command-line tool.** As in EXP-021, our runner reads the mission files itself.
  - It pairs scans with IMU samples using upstream's own `_ScanBuffer`.
  - It passes the Hesai per-point times relative to the scan start, which is upstream's convention for this LiDAR.
  - It reorders the IMU columns to upstream's order.
  - It applies the offset by shifting the integer nanosecond timestamps, as lightning-lm's bag converter does. The first shifted IMU timestamp of ARC-6 equals the bag's to the nanosecond.
- **One LiDAR.** GenZ-LIO uses the Hesai only, as SE(3)-LVIO S8 does. S9a also uses the Livox, so comparisons across systems should pair configs with the same sensors.
- **Three dev missions and one host,** as in EXP-000.

## Failures

None: 15 of 15 runs are `ok`, and none ran from uncommitted code (repo commit 3417882, GenZ-LIO commit 0936d34). The GenZ-LIO container image was rebuilt from 0936d34 before the run. Each run's `summary.json` records the offset it used (for example −0.0065 s on ARC-6). None of our other jobs ran on the host during the run.

## Reproduce

<!-- lvx:begin reproduce -->
```bash
lvx run EXP-022 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-022                  # runs.csv + summary.json
lvx figures EXP-022
lvx viewer EXP-022                # on the host: map + trajectories for the 3D viewer
lvx report EXP-022
```

What `lvx run` executed for each variant (repeat 1; all runs are in `results/manifests/`):

**baseline** (from `.`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim)):

```bash
podman run --rm -v "$MISSION":/mission:ro -v "$OUT":/out "$IMAGE" bash -c 'taskset -c 0-3 python3 lvio_exp/run_comfort.py /mission/comfort_offline /out/config.yaml /out --name arc-6 --imu-dt -0.0065' > "$OUT/run.log" 2>&1 && python3 systems/se3-lvio/tools/to_prism.py "$MISSION/comfort_offline/calib.json" "$OUT/arc-6_imu.tum" "$OUT/estimate.tum"
```
<!-- lvx:end reproduce -->
