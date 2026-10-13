# LVIO_exp

**What actually matters in LiDAR-inertial(-visual) odometry? A controlled, pre-registered ablation study of
[SE(3)-LVIO](https://github.com/url-kaist/se3-livom-comfort) and
[lightning-lm](https://github.com/gaoxiang12/lightning-lm) on GrandTour / COMFORT data.**

[![CI](https://github.com/Munna-Manoj/LVIO_exp/actions/workflows/ci.yml/badge.svg)](https://github.com/Munna-Manoj/LVIO_exp/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-site-0f9d8a)](https://munna-manoj.github.io/LVIO_exp/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[![EIG-2 (Eigergletscher, GrandTour): the map SE(3)-LVIO builds, with its trajectory on the GT prism path](docs/assets/experiments/EXP-000/viewer/eig-2.gif)](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-000&mission=eig-2)

*EIG-2 from EXP-000: the map rebuilt from SE(3)-LVIO's estimate (LIO baseline, repeat 1), white = GT prism.
[Open it in 3D](https://munna-manoj.github.io/LVIO_exp/viewer/?exp=EXP-000&mission=eig-2). Data: [GrandTour](https://huggingface.co/datasets/leggedrobotics/grand_tour_dataset)
(MIT; Frey, Tuna et al., [arXiv:2602.18164](https://arxiv.org/abs/2602.18164)).*

> [!NOTE]
> Status: **foundation (M0)**. The harness, protocol and 20 experiment specs are in place; no
> experiment has run inside the harness yet, so this page shows no result numbers. See the
> [roadmap](ROADMAP.md).

---

## Two tracks, one codebase

- **The course:** learn LiDAR-visual-inertial SLAM step by step, following the book
  [*SLAM in Autonomous Driving*](https://github.com/gaoxiang12/slam_in_autonomous_driving):
  - from IMU-only through ESKF, preintegration, factor graphs and robust estimation;
  - then point clouds, LiDAR odometry and LIO;
  - then mapping and loop closure;
  - beyond the book to the camera (LVIO);
  - and a **capstone** on SE(3)-LVIO, lightning-lm and GenZ-LIO.

  Every chapter has a Python track that runs without data, a C++ lab on the book's official code and
  datasets, and links to the ablations.
- **The study:** pre-registered ablations of SE(3)-LVIO, lightning-lm and GenZ-LIO on real GrandTour data.

```mermaid
flowchart LR
  A[A math] --> B[B IMU, ESKF,<br/>preintegration,<br/>graphs, robust] --> C[C point clouds,<br/>NN structures,<br/>2D SLAM] --> D[D LiDAR odometry,<br/>loose LIO] --> E[E tight LIO] --> F[F mapping,<br/>loops, localisation]
  E --> G[G camera, LVIO,<br/>evaluation] --> X[X capstone:<br/>lightning-lm, SE3-LVIO,<br/>ablation study]
  F --> X
```

![30 IMU-only runs fanning out around the true figure-eight](course/chapters/B01-imu-propagation/results/drift_3d.png)

*From course chapter [B01](course/chapters/B01-imu-propagation/): why every LIO system needs more than its IMU. Every chapter is one folder you can read and run on its own.*

## Why this repository exists

- **One protocol, three systems.** Every system runs on the same missions, cores, frame conversion and ATE code.
- **Every experiment is written before its data.** Question, hypothesis, prediction and decision rule are
  hashed (`spec.lock`) before the first run. Negative results stay.
- **Effects must beat noise.** A change counts only if it moves ATE by more than 2σ of run-to-run noise
  (EXP-000).
- **Every number traces back** to a run manifest: commits, config hash, container digest, host.

```mermaid
flowchart LR
  spec[pre-registered spec] --> run[lvx run<br/>three systems, pinned cores]
  run --> eval[lvx eval<br/>COMFORT ATE, prism frame]
  eval --> noise{beats 2σ noise?}
  noise --> report[generated report<br/>+ figures + 3D viewer]
```

## Experiments

<!-- lvx:begin index -->
| ID | Question | Phase | Status | Verdict | Headline |
|---|---|---|---|---|---|
| [EXP-000](docs/experiments/EXP-000-baselines-and-noise-floor.md) | How large is run-to-run noise, and do the pre-repo baselines reproduce? | P0 | ✅ concluded | 🟢 adopt | noise floor: σ ≤ 0.0053 ate_rmse_cm per cell |
| [EXP-001](docs/experiments/EXP-001-chi2-gate-sweep.md) | How wide should the residual gate be? | P1 | 🗒️ planned |  |  |
| [EXP-002](docs/experiments/EXP-002-robust-kernels-iekf.md) | Does a robust kernel in the scan update beat a hard limit alone? | P1 | 🗒️ planned |  |  |
| [EXP-003](docs/experiments/EXP-003-gnc-tls-iekf.md) | Does gradually rejecting outliers across the update iterations help? | P1 | 🗒️ planned |  |  |
| [EXP-004](docs/experiments/EXP-004-robust-photometric.md) | Does a robust kernel on the camera residuals make the camera useful? | P5 | 🗒️ planned |  |  |
| [EXP-005](docs/experiments/EXP-005-degeneracy-projection.md) | Does skipping poorly constrained directions in the update help? | P2 | 🗒️ planned |  |  |
| [EXP-006](docs/experiments/EXP-006-step-limits-cov-hygiene.md) | Do update safeguards change accuracy, or only robustness? | P2 | 🗒️ planned |  |  |
| [EXP-007](docs/experiments/EXP-007-smoke-filter.md) | Does dropping weak, close returns remove smoke without hurting accuracy? | P3 | 🗒️ planned |  |  |
| [EXP-008](docs/experiments/EXP-008-keyframe-map-insertion.md) | Should the map be updated every scan or only at keyframes? | P3 | 🗒️ planned |  |  |
| [EXP-009](docs/experiments/EXP-009-se3-vs-so3xr3.md) | Does the coupled SE(3) pose update matter? | P4 | 🗒️ planned |  |  |
| [EXP-010](docs/experiments/EXP-010-state-17-vs-12.md) | Does estimating accelerometer bias and gravity online pay off? | P4 | 🗒️ planned |  |  |
| [EXP-011](docs/experiments/EXP-011-online-time-offset-lever-arm.md) | Can online estimation replace the hand-fitted IMU time offset? | P4 | 🗒️ planned |  |  |
| [EXP-012](docs/experiments/EXP-012-image-quality-gate.md) | Does skipping bad camera frames make the camera pay for itself? | P5 | 🗒️ planned |  |  |
| [EXP-013](docs/experiments/EXP-013-affine-brightness.md) | Does brightness compensation help the camera update? | P5 | 🗒️ planned |  |  |
| [EXP-014](docs/experiments/EXP-014-drift-and-loop-closure.md) | Is there drift worth closing loops for? | P5 | 🗒️ planned |  |  |
| [EXP-015](docs/experiments/EXP-015-gnc-pgo-false-loops.md) | Does GNC protect the pose graph from false loops? | P6 | 🗒️ planned |  |  |
| [EXP-016](docs/experiments/EXP-016-point-budget-sweep.md) | How much accuracy does each millisecond of scan time buy? | P7 | 🗒️ planned |  |  |
| [EXP-017](docs/experiments/EXP-017-four-core-budget.md) | Do all three systems hold 10 Hz and 20 Hz on four cores? | P7 | 🗒️ planned |  |  |
| [EXP-018](docs/experiments/EXP-018-stress-suite.md) | Which design choices matter when the data gets worse? | P6 | 🗒️ planned |  |  |
| [EXP-019](docs/experiments/EXP-019-lightning-tuning-fairness.md) | Is lightning-lm tuned fairly? | PX | 🗒️ planned |  |  |
| [EXP-020](docs/experiments/EXP-020-map-structure-speed.md) | Does the map data structure set the speed? | P3 | 🗒️ planned |  |  |
| [EXP-021](docs/experiments/EXP-021-genz-lio-baseline-and-noise-floor.md) | How large is GenZ-LIO's run-to-run noise, and does the harness run it correctly? | P0 | ✅ concluded | 🟢 adopt | superseded by EXP-022 |
| [EXP-022](docs/experiments/EXP-022-genz-lio-baseline-with-imu-offset.md) | How large is GenZ-LIO's run-to-run noise, with the protocol's IMU time offset? | P0 | ✅ concluded | 🟢 adopt | noise floor: σ ≤ 0.0000 ate_rmse_cm per cell |
| [EXP-023](docs/experiments/EXP-023-pid-adaptive-voxel-size.md) | Should the point budget grow with the scene's size? | P7 | 🗒️ planned |  |  |
| [EXP-024](docs/experiments/EXP-024-point-to-point-fallback.md) | Should points without a plane get a point-to-point residual? | P3 | 🗒️ planned |  |  |
| [EXP-025](docs/experiments/EXP-025-point-to-point-candidate-pruning.md) | Does thinning GenZ-LIO's point-to-point candidates cost accuracy? | P3 | 🗒️ planned |  |  |
| [EXP-026](docs/experiments/EXP-026-genz-lio-tuning-fairness.md) | Is GenZ-LIO tuned fairly? | PX | 🗒️ planned |  |  |
<!-- lvx:end index -->

## The three systems

| | SE(3)-LVIO | lightning-lm (LIO frontend) | GenZ-LIO |
|---|---|---|---|
| Filter | iterated ESKF, SE(3) pose retraction, 17-dim error state | iterated ESKF, SO(3)×R³, 12-dim (accel bias + gravity fixed) | iterated ESKF, SO(3)×R³ (IKFoM, as FAST-LIO) |
| Map | probabilistic voxel planes (VoxelMap) | iVox, 5-NN plane fit | octree voxel planes + point candidates, voxel-pruned search |
| Residual weight | point + plane covariance, 3σ gate | constant weight, degeneracy projection | point-to-plane + point-to-point, each covariance-weighted and gated |
| Downsampling | voxel size adjusted each scan to keep about 2000 plane-matched points | fixed voxel | voxel size set by a PID controller on a point target that grows with the scene's size |
| Sensors | 2 LiDARs + IMU + camera (photometric) | 1 LiDAR + IMU | 1 LiDAR + IMU |
| Backend | plane BA (HBA) + iSAM2 | loop closure + pose graph (not used here) | none |
| Included as | fork, submodule; ablations in it | private fork, cloned at build time; ablations in it (no licence: never published, [ADR-0013](docs/process/decisions/ADR-0013-lightning-lm-private-fork.md)) | fork, submodule; ablations in it ([ADR-0012](docs/process/decisions/ADR-0012-genz-lio-third-system.md)) |

## Explore

| | |
|---|---|
| 📊 [Experiment reports](docs/experiments/index.md) | question → setup → results → verdict |
| 🧭 [Roadmap](ROADMAP.md) | milestones and the experiment plan |
| 📚 [Learn](docs/learn/README.md) | the course, book-aligned. Start with [B01 IMU propagation](course/chapters/B01-imu-propagation/) |
| 💾 [Get the data](docs/how-to/get-the-data.md) | official links for the SAD datasets and GrandTour |
| 💡 [Explanation](docs/explain/README.md) | e.g. [SE(3) vs SO(3)×R³](docs/explain/se3-vs-so3xr3.md), [outliers in an IEKF](docs/explain/outliers-in-an-iekf.md) |
| 🛠️ [How-to](docs/how-to/README.md) | set up, propose and run an experiment |
| 📐 [Protocol](docs/process/EXPERIMENT_PROTOCOL.md) | the rules every experiment follows |

## Quick start

```bash
git clone --recurse-submodules https://github.com/Munna-Manoj/LVIO_exp.git && cd LVIO_exp
pip install -e ".[dev]"
lvx init --data-root ~/datasets/lvx --run-root ~/lvx_runs   # this machine only (git-ignored lvx.local.yaml)
lvx data check                     # which datasets are ready, and which chapters use them
lvx exp list                       # the experiment plan
python tools/check_experiments.py  # check_experiments: OK (22 experiments)
```

Running experiments needs the GrandTour data and the compute host: see [Set up](docs/how-to/setup.md).

## Credits

- **SE(3)-LVIO** (COMFORT entry, GPL-2.0) builds on VoxelMap, FAST-LIVO2 and HBA from HKU MARS.
- **lightning-lm** by Gao Xiang et al. It has no licence. We modify it for research in a private fork, which
  is cloned at build time and never published or redistributed; the reports describe each change in words
  ([ADR-0013](docs/process/decisions/ADR-0013-lightning-lm-private-fork.md)).
- **Course backbone:** [*SLAM in Autonomous Driving*](https://github.com/gaoxiang12/slam_in_autonomous_driving)
  by Gao Xiang et al. (code MIT; the book is linked, never copied).
- **Data:** [GrandTour](https://grand-tour.leggedrobotics.com/) and the COMFORT localization benchmark, plus the
  SAD datasets (NCLT, UrbanLoco, UTBM, WXB, 2dmapping, AVIA). See [Get the data](docs/how-to/get-the-data.md).
- **Repository structure and writing guide:** adapted from [DS-MSP](https://github.com/Munna-Manoj/DS-MSP).

## License

MIT for this repository's own code and docs ([LICENSING.md](LICENSING.md)). The systems under test keep
their own licences.
