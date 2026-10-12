# EXP-021 — How large is GenZ-LIO's run-to-run noise, and does the harness run it correctly?

**TL;DR:** adopt: all 15 GenZ-LIO runs are ok, bit-for-bit deterministic (σ = 0, so its noise floor is the 0.005 cm minimum), cover ≥ 0.9994 of the scans, and score 1.382 cm on ARC-6 (bound 3 cm), 2.506 cm on EIG-2 and 5.884 cm on SNOW-3.

> [!WARNING]
> **Superseded by [EXP-022](EXP-022-genz-lio-baseline-with-imu-offset.md) (2026-10-12).** After this experiment was concluded we found that its runs lacked the per-mission IMU time offset (`configs/missions.yaml` `imu_dt`, −4.8 to −6.5 ms), which the protocol gives every system (CLAUDE.md §3). The verdict below stands as recorded, but these numbers are not comparable with EXP-000's. GenZ-LIO's baseline and noise floor come from EXP-022.

<!-- lvx:begin status -->
**Status:** ✅ concluded · verdict **🟢 adopt** · **Phase:** P0 (Foundation: baselines and noise floor) · **System:** `genz-lio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | How much does ATE vary between identical runs of GenZ-LIO stock on the dev missions, and does the harness run it without dropping scans or mis-placing the LiDAR? |
| **Hypothesis** | GenZ-LIO's worker threads (correspondence search and map updates, runtime.max_threads 4) combine their results in a fixed order on an offline replay, as SE(3)-LVIO's frontend does (EXP-000), so its runs are deterministic or nearly so. With upstream's Hesai template and the GrandTour extrinsic it tracks every dev mission at centimetre level. |
| **Prediction** | σ(ATE) per mission below 0.05 cm. Every run has pose_coverage ≥ 0.99. ATE on ARC-6 below 3 cm (one scratch smoke run while integrating gave 1.38 cm; it informed this bound and is not a result). EIG-2 and SNOW-3 are measured only; no bound is predicted there. |
| **Falsified if** | any run has pose_coverage below 0.99, any run fails, or ARC-6 ATE is 3 cm or more. Each means the harness or the config is wrong for GenZ-LIO (frame, extrinsic, timestamps, or core budget). |
| **Decision rule** | pass (verdict adopt = GenZ-LIO runs correctly in the harness) if all 15 runs are ok with pose_coverage ≥ 0.99 and the ARC-6 mean ATE is below 3 cm; otherwise reject and fix the runner or config before any experiment uses GenZ-LIO. The σ per mission from this experiment is GenZ-LIO's noise floor for all later experiments (ADR-0004, ADR-0012). |

<sub>Fields above are pre-registered (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | genz_stock as is |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 5 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_median_cm`, `ate_max_cm`, `ms_mean`, `ms_p95`, `rss_mb`, `pose_coverage`
- **Commits:** repo fbfe8690af · system 82328f5937
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
Primary metric `ate_rmse_cm`: mean ± std over repeats. Δ is against `baseline` on the same mission; the effect is called only when |Δ| > 2σ of run-to-run noise (σ from this experiment).

| Mission | Variant | ate_rmse_cm | Δ | Effect | ms p95 | runs ok / failed |
|---|---|---|---|---|---|---|
| arc-6 | `baseline` | 1.382 ± 0.000 |  |  | 37.8 | 5 / 0 |
| eig-2 | `baseline` | 2.506 ± 0.000 |  |  | 70.6 | 5 / 0 |
| snow-3 | `baseline` | 5.884 ± 0.000 |  |  | 66.7 | 5 / 0 |

![pareto](../assets/experiments/EXP-021/pareto.png)

### Maps

Map rebuilt from the baseline's repeat-1 estimate, all repeat-1 trajectories, in the GT frame (`lvx viewer`). Open a mission in the [interactive 3D viewer](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-021) to orbit, hide the ceiling and toggle trajectories. Data: [GrandTour](https://huggingface.co/datasets/leggedrobotics/grand_tour_dataset) (MIT; Frey, Tuna et al., [arXiv:2602.18164](https://arxiv.org/abs/2602.18164)).

[![arc-6: map and trajectories](../assets/experiments/EXP-021/viewer/arc-6_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-021&mission=arc-6)

[![eig-2: map and trajectories](../assets/experiments/EXP-021/viewer/eig-2_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-021&mission=eig-2)

[![snow-3: map and trajectories](../assets/experiments/EXP-021/viewer/snow-3_map.png)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-021&mission=snow-3)
<!-- lvx:end results -->

- **Runs repeat exactly.** σ = 0.000 cm on all three missions (Results table); the five `estimate.tum` files of each mission have the same md5.
- **ARC-6 at 1.382 cm,** inside the pre-registered 3 cm bound. For orientation, on the same mission EXP-000 measured SE(3)-LVIO S8 at 0.805 cm and lightning-lm at 1.407 (indoor) and 1.639 cm (stock).
- **The field missions are tracked.** 2.506 cm on EIG-2, close to S8's 2.489 cm, where lightning-lm drifted to 294–465 cm in EXP-000; 5.884 cm on SNOW-3, about 4.7 × S8's 1.265 cm (Results table; EXP-000 for the other systems).
- **Coverage.** Every run keeps ≥ 0.9994 of the scans in the IMU span; every run skips exactly one scan at the start, which GenZ-LIO reports as not valid yet (runner `summary.json`: `skipped: 1`), and the first valid scan initialises the filter (0 ms in `timing.csv`).
- **Cost on 4 cores.** ms p95 37.8 (arc-6), 70.6 (eig-2), 66.7 (snow-3); RSS 0.46, 2.6 and 1.4 GB (pareto.png, `summary.json`). ARC-6 per-scan time is close to S8's (ms_mean 32.0 vs 27.4 in EXP-000).

## Discussion

Determinism, as for SE(3)-LVIO in EXP-000: the input is replayed offline in the same order every time, and GenZ-LIO's worker threads (correspondence search and map updates, 4 here) evidently combine their results in a fixed order, so every run computes the same floating-point numbers. We have not traced how. The consequence (ADR-0004, ADR-0012) is that GenZ-LIO variants are judged against the 0.005 cm floor: a change of more than 0.01 cm counts as an effect, so later reports should also ask whether an effect is consistent across missions.

GenZ-LIO keeps tracking on the glacier (EIG-2) where lightning-lm lost it. GenZ-LIO's paper motivates its two main ideas by such scenes: open spaces with few planes, where it falls back on point-to-point residuals, and a point budget that adapts the voxel size to the scene scale. Which idea carries it there is a question for the ablations (M0.8), not for this experiment. Why it is 4.7 × worse than SE(3)-LVIO on SNOW-3 is also open; the coupled SE(3) state, the probabilistic plane map and the second LiDAR are all candidates (EXP-009 for the state; background in [SE(3) vs SO(3)×R³](../explain/se3-vs-so3xr3.md)).

## Verdict

**Adopt: GenZ-LIO runs correctly in the harness.** The frozen rule asks for all 15 runs ok with pose_coverage ≥ 0.99 and an ARC-6 mean ATE below 3 cm. All 15 are ok, the lowest coverage is 0.9994, and ARC-6 is 1.382 cm. The σ per mission (0 everywhere, so the 0.005 cm floor) is now GenZ-LIO's noise floor; `lvx eval` takes it from this experiment for every `genz_stock` baseline (`noise_floor` in summary.json).

## Threats to validity

- **The 3 cm bound was informed by a scratch run.** One smoke run while integrating gave 1.382 cm on ARC-6, and the spec says so. The bound was set at about twice that, so the pass is not in doubt, but it is not a blind prediction. The result equals the smoke run exactly, as determinism implies.
- **Stock, not tuned.** `genz_stock` is upstream's Hesai template with only platform keys changed; upstream tuned per sequence for its own benchmarks. The SNOW-3 gap may shrink with tuning on dev; that is a fairness experiment (like EXP-019), not this one.
- **Our runner, not upstream's CLI.** The runner reads `comfort_offline/` itself. It uses upstream's own `_ScanBuffer` for the scan–IMU pairing, passes Hesai per-point times relative to the scan start (upstream's convention for this LiDAR type) and reorders the IMU columns to upstream's order. A wrong convention would bend trajectories; ARC-6 at 1.4 cm and EIG-2 at 2.5 cm make that unlikely but do not prove each step.
- **One LiDAR.** GenZ-LIO uses the Hesai only, SE(3)-LVIO S8 too (S9a adds the Livox). Cross-system comparisons should pair like with like.
- **Three dev missions, one host,** as in EXP-000.
- **Protocol deviation (found after concluding).** The runner read `imu.txt` without the per-mission `imu_dt` that SE(3)-LVIO's script and the lightning-lm bags apply. A 5–6.5 ms IMU–LiDAR misalignment biases motion prediction and deskewing in fast turns, so the numbers here may differ from GenZ-LIO's under the protocol. Fixed in the fork (pin 0936d34) and `lvx/runner.py`; rerun as EXP-022.

## Failures

None: 15 of 15 runs `ok`, none dirty (repo fbfe869, system 82328f5, both clean). None of our other jobs ran on the host during the run.

## Reproduce

<!-- lvx:begin reproduce -->
```bash
lvx run EXP-021 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-021                  # runs.csv + summary.json
lvx figures EXP-021
lvx viewer EXP-021                # on the host: map + trajectories for the 3D viewer
lvx report EXP-021
```

What `lvx run` executed for each variant (repeat 1; all runs are in `results/manifests/`):

**baseline** (from `.`; `$OUT` = this run's directory: <run_root>/<EXP>/<variant>/<mission>/r<k>, `$GRANDTOUR` = dataset `grandtour` (configs/datasets.yaml), `$MISSION` = the mission folder inside $GRANDTOUR, `$IMAGE` = the system's container image (systems/systems.yaml; local tag in lvx.local.yaml), `$PATH` = the caller's PATH, after the machine's own tool folders (lvx.local.yaml `path`, e.g. a docker shim)):

```bash
podman run --rm -v "$MISSION":/mission:ro -v "$OUT":/out "$IMAGE" bash -c 'taskset -c 0-3 python3 lvio_exp/run_comfort.py /mission/comfort_offline /out/config.yaml /out --name arc-6' > "$OUT/run.log" 2>&1 && python3 systems/se3-lvio/tools/to_prism.py "$MISSION/comfort_offline/calib.json" "$OUT/arc-6_imu.tum" "$OUT/estimate.tum"
```
<!-- lvx:end reproduce -->
