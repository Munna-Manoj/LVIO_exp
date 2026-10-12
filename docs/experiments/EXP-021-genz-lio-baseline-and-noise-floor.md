# EXP-021 — How large is GenZ-LIO's run-to-run noise, and does the harness run it correctly?

**TL;DR:** abandoned, superseded by [EXP-022](EXP-022-genz-lio-baseline-with-imu-offset.md): the runner left out the per-mission IMU time offset (−4.8 to −6.5 ms) that the protocol gives every system, so these 15 runs (all ok, deterministic, ARC-6 1.382 cm) are not comparable with EXP-000.

<!-- lvx:begin status -->
**Status:** ⛔ abandoned · **Phase:** P0 (Foundation: baselines and noise floor) · **System:** `genz-lio` · **Depends on:** EXP-000
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

- **All 15 runs ok and deterministic:** σ = 0.000 cm per mission; the five `estimate.tum` files of each mission have the same md5.
- **Without the IMU offset:** ARC-6 1.382 cm, EIG-2 2.506 cm, SNOW-3 5.884 cm (Results table); lowest pose_coverage 0.9994.
- These numbers are kept as the record of what was run. They are not GenZ-LIO's baseline: EXP-022 measures it under the full protocol.

## Discussion

The protocol gives every system the per-mission IMU time offset `imu_dt` from `configs/missions.yaml` (CLAUDE.md §3): SE(3)-LVIO's run script applies it, and the lightning-lm bags were written with it (their first IMU stamp is 6.5 ms before `imu.txt`'s on ARC-6, that mission's `imu_dt`). The GenZ-LIO runner written for this experiment read `imu.txt` unshifted, and `lvx` did not pass the offset. The gap was found while writing the GenZ-LIO arm of EXP-011 (online time offset), after the runs. A 5–6.5 ms misalignment between IMU and LiDAR biases the motion prediction and deskewing in fast turns, so the numbers above may be slightly off from what GenZ-LIO achieves under the protocol.

## Verdict

**None: abandoned.** By its numbers the frozen rule would have passed (15/15 ok, coverage ≥ 0.9994, ARC-6 1.382 < 3 cm), but the runs did not follow the evaluation protocol, so no verdict is drawn from them. The fix is in the fork (pin 0936d34, `--imu-dt`) and in `lvx/runner.py`; EXP-022 repeats the same plan with it.

## Threats to validity

- The point of abandoning is to avoid publishing GenZ-LIO numbers produced under a different protocol than the other systems'. If the offset turns out to change nothing (EXP-022 equal to EXP-021), the abandonment cost one rerun and nothing else.

## Failures

No run failed or was dirty. The whole experiment is set aside for the protocol deviation above (IMU time offset not applied).

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
