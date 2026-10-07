# Learn: LiDAR-visual-inertial SLAM, from first principles to real systems

A hands-on course that follows the book **[SLAM in Autonomous Driving](https://github.com/gaoxiang12/slam_in_autonomous_driving)**
(SAD, Gao Xiang et al.; [English PDF](https://github.com/gaoxiang12/slam-in-ad-en/blob/main/sad-en.pdf)).
Where the book stops short of what modern LIO systems need, **🔗 bridge chapters** (I01–I07) fill the gap,
on the SAD datasets and on GrandTour. The course then goes beyond the book to the camera and to honest
evaluation, and ends with a **capstone** on two real systems, lightning-lm and SE(3)-LVIO, plus the
[ablation study](../experiments/index.md).

## Three ways to learn each idea

| Track | What you do | Runs on | Needs |
|---|---|---|---|
| **Build it** (Python) | read and run one self-contained folder: a README with the maths, and Python that mirrors it line by line | synthetic data you can picture | a laptop, nothing else |
| **Run it in C++** (SAD lab) | run the book's official C++ implementation on the official datasets | SAD datasets | the SAD container + data ([Get the data](../how-to/get-the-data.md)) |
| **On real data** (Python) | run your own code on SAD bags or GrandTour; required in every 🔗 bridge chapter | SAD datasets, GrandTour | the data + `pip install -e ".[data]"` |
| **Test it at scale** (ablation) | see the same idea switched on and off inside SE(3)-LVIO / lightning-lm | GrandTour | the reference host |

> [!TIP]
> **Every chapter stands alone.** Open one folder, read its README, run `python main.py`. No shared library,
> no hidden helpers: if a chapter needs a rotation function from an earlier one, it has its own copy.
> The Python track needs no download at all. The C++ labs
> show what the idea looks like in a fast, real implementation. The ablations show whether it matters on
> a real robot.

## The learning path

The book's order is itself a gradual integration ladder. Each rung adds one sensor or one idea to the last:

```mermaid
flowchart LR
  A[A · Math<br/>rotations, KF] --> B1[B01 IMU only] --> I1[🔗 I01 real IMUs,<br/>Allan variance] --> B2[B02 IMU + GNSS<br/>ESKF] --> I2[🔗 I02 time offsets,<br/>extrinsics]
  I2 --> B4[B03–B05 preintegration,<br/>factor graphs, robust estimation]
  B4 --> C[C · point clouds,<br/>NN structures, 2D SLAM]
  C --> D3[D03 LiDAR only] --> I3[🔗 I03 degeneracy] --> D4[D04 loosely coupled LIO]
  D4 --> E2[E02 tightly coupled LIO] --> I4[🔗 I04 map structures<br/>in the loop] --> I5[🔗 I05 multi-LiDAR]
  I5 --> F[F01–F02 mapping,<br/>loop closure] --> I6[🔗 I06 online backend] --> I7[🔗 I07 dynamic objects]
  I7 --> G2[G02 LVIO<br/>+ camera] --> X[X · capstone<br/>lightning-lm, SE3-LVIO,<br/>ablation study]
```

## Chapters

Generated from [`course/curriculum.yaml`](https://github.com/Munna-Manoj/LVIO_exp/blob/main/course/curriculum.yaml). Linked titles are available now.

<!-- course:begin curriculum -->
### Part A · Mathematical foundations  <sub>(SAD ch. 2)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| A01 | Rotations and poses: SO(3), SE(3), Exp/Log, boxplus, Jacobians | a rotating box: local vs global perturbation; the pose 'banana' | – | [EXP-009](../experiments/EXP-009-se3-vs-so3xr3.md) | ⬜ |
| A02 | From the Kalman filter to the error-state Kalman filter | a cart on a rail, then a unicycle: ±3σ band, shrinking ellipses | – | – | ⬜ |

### Part B · Inertial and integrated navigation  <sub>(SAD ch. 3, 4)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| B01 | [IMU propagation: why IMU-only odometry drifts, and how fast](B01-imu-propagation/index.md) | a 3D figure-eight: IMU-only runs fanning out | – | [EXP-010](../experiments/EXP-010-state-17-vs-12.md), [EXP-011](../experiments/EXP-011-online-time-offset-lever-arm.md) | ✅ |
| I01 | 🔗 Real IMUs: noise densities, bias instability and Allan variance (vehicle IMU vs STIM320) | a still IMU for hours: Allan-deviation slopes −½, 0, +½ | ulhk, grandtour | [EXP-010](../experiments/EXP-010-state-17-vs-12.md) | ⬜ |
| B02 | ESKF with GNSS: the first fusion filter | a car on a stadium track, 1 Hz GNSS, a 30 s outage: error sawtooth | – | [EXP-010](../experiments/EXP-010-state-17-vs-12.md) | ⬜ |
| I02 | 🔗 Time offsets, lever arms and extrinsics: estimate them, or pay in centimetres | the stadium track with a 50 ms time offset and a 1 m lever arm | builtin, grandtour | [EXP-011](../experiments/EXP-011-online-time-offset-lever-arm.md), [EXP-018](../experiments/EXP-018-stress-suite.md) | ⬜ |
| B03 | IMU preintegration: one factor for a hundred samples | two keyframes, 200 IMU samples → one relative-motion arrow | – | – | ⬜ |
| B04 | Factor graphs: GINS as an optimisation problem | a square of 5 poses + 1 loop (Pose2SLAM), then M3500 | – | [EXP-014](../experiments/EXP-014-drift-and-loop-closure.md) | ⬜ |
| B05 | Robust estimation: gates, M-estimators (IRLS), RANSAC and GNC | a line with 50 % outliers: loss and weight curves, RANSAC, GNC | – | [EXP-001](../experiments/EXP-001-chi2-gate-sweep.md), [EXP-002](../experiments/EXP-002-robust-kernels-iekf.md), [EXP-003](../experiments/EXP-003-gnc-tls-iekf.md), [EXP-015](../experiments/EXP-015-gnc-pgo-false-loops.md) | ⬜ |

### Part C · Point clouds, nearest neighbours and 2D LiDAR SLAM  <sub>(SAD ch. 5, 6)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| C01 | Point clouds: scan patterns, motion distortion, deskewing, downsampling | a spinning 16-line LiDAR in a box room: bent wall, then deskewed | – | [EXP-016](../experiments/EXP-016-point-budget-sweep.md) | ⬜ |
| C02 | Nearest-neighbour structures and speed: grid, kd-tree, octree, ikd-tree, iVox, VoxelMap | 10⁴–10⁶ room points: query time vs N; kd-tree cells in 2D | – | [EXP-008](../experiments/EXP-008-keyframe-map-insertion.md), [EXP-020](../experiments/EXP-020-map-structure-speed.md) | ⬜ |
| C03 | Line and plane fitting, and the uncertainty of a plane | a noisy plane patch: eigenvalue bars, normal-uncertainty cone | – | [EXP-001](../experiments/EXP-001-chi2-gate-sweep.md) | ⬜ |
| C04 | 2D scan matching: ICP and likelihood fields | an L-shaped 2D room: ICP iterations, likelihood-field heatmap | – | – | ⬜ |
| C05 | 2D mapping: occupancy grids, submaps and loop closure | a ray-cast corridor loop: occupancy grid before/after loop closure | – | – | ⬜ |

### Part D · 3D LiDAR odometry and loosely coupled LIO  <sub>(SAD ch. 7)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| D01 | 3D registration: point-to-point, point-to-line, point-to-plane ICP | Stanford bunny: error vs iteration, basin of convergence | – | [EXP-001](../experiments/EXP-001-chi2-gate-sweep.md) | ⬜ |
| D02 | NDT: registration against a map of Gaussians | the voxelised room: per-voxel Gaussians, NDT score surface | – | [EXP-020](../experiments/EXP-020-map-structure-speed.md) | ⬜ |
| D03 | LiDAR-only odometry: NDT LO, incremental NDT, LOAM-like features, and degeneracy | the Courtyard corridor: Hessian eigenvalue dip, drift along the corridor | – | [EXP-005](../experiments/EXP-005-degeneracy-projection.md) | ⬜ |
| I03 | 🔗 Degeneracy: when the geometry cannot constrain the pose (corridors, open fields) | corridor + open field: constraint ellipsoids drawn on the map | ulhk, grandtour | [EXP-005](../experiments/EXP-005-degeneracy-projection.md), [EXP-006](../experiments/EXP-006-step-limits-cov-hygiene.md) | ⬜ |
| D04 | Loosely coupled LIO: an ESKF that takes LO poses | the Courtyard: position covariance with vs without LiDAR | – | – | ⬜ |

### Part E · Tightly coupled LIO  <sub>(SAD ch. 8)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| E01 | The iterated EKF is Gauss-Newton with a prior | one range measurement: EKF vs IEKF iterates walking to the optimum | – | [EXP-009](../experiments/EXP-009-se3-vs-so3xr3.md) | ⬜ |
| E02 | Tightly coupled LIO with an IEKF (a mini FAST-LIO) | the Courtyard: map coloured by point-to-plane residual | – | [EXP-001](../experiments/EXP-001-chi2-gate-sweep.md), [EXP-006](../experiments/EXP-006-step-limits-cov-hygiene.md), [EXP-010](../experiments/EXP-010-state-17-vs-12.md) | ⬜ |
| I04 | 🔗 Map structures in the loop: kd-tree vs ikd-tree vs iVox vs VoxelMap inside your LIO | the Courtyard: memory and query time vs map size, per structure | nclt, grandtour | [EXP-008](../experiments/EXP-008-keyframe-map-insertion.md), [EXP-016](../experiments/EXP-016-point-budget-sweep.md), [EXP-020](../experiments/EXP-020-map-structure-speed.md) | ⬜ |
| I05 | 🔗 Multi-LiDAR fusion: two scanners, two noise models, one map | two LiDARs: a 'doubled' wall before/after extrinsic calibration | grandtour | [EXP-000](../experiments/EXP-000-baselines-and-noise-floor.md), [EXP-018](../experiments/EXP-018-stress-suite.md) | ⬜ |
| E03 | Preintegration-based LIO: the optimisation alternative | the Courtyard, sliding window: biases converging | – | – | ⬜ |

### Part F · Mapping, loop closure and localisation  <sub>(SAD ch. 9, 10)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| F01 | Offline mapping: frontend, backend, map optimisation | three laps of the Courtyard: blurred vs crisp walls | – | [EXP-014](../experiments/EXP-014-drift-and-loop-closure.md) | ⬜ |
| F02 | Loop closure: candidates, verification, and a robust pose graph | M3500 / sphere with fake loops: L2 collapses, a robust kernel survives | – | [EXP-014](../experiments/EXP-014-drift-and-loop-closure.md), [EXP-015](../experiments/EXP-015-gnc-pgo-false-loops.md) | ⬜ |
| I06 | 🔗 An online smoothing backend: keyframe windows, plane bundle adjustment, iSAM2-style updates | room planes seen from many poses: plane thickness before/after BA | nclt, grandtour | [EXP-014](../experiments/EXP-014-drift-and-loop-closure.md) | ⬜ |
| I07 | 🔗 Dynamic objects and map hygiene: people, cars, smoke, and free-space carving | a box 'car' crossing the room: ghost trail, removed by ray carving | ulhk, grandtour | [EXP-007](../experiments/EXP-007-smoke-filter.md), [EXP-008](../experiments/EXP-008-keyframe-map-insertion.md) | ⬜ |
| F03 | Localisation in a prior map: tiles, initial search, EKF fusion | kidnapped in the Courtyard map: score heatmap over (x, y) | – | – | ⬜ |

### Part G · Beyond the book: camera, LVIO, evaluation  <sub>(SAD ch. –)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| G01 | Direct photometric alignment: patches, pyramids, exposure | a textured wall: photometric cost vs shift, coarse-to-fine basin | – | [EXP-004](../experiments/EXP-004-robust-photometric.md), [EXP-012](../experiments/EXP-012-image-quality-gate.md), [EXP-013](../experiments/EXP-013-affine-brightness.md) | ⬜ |
| G02 | LVIO: adding the camera to a LiDAR-inertial filter | the Courtyard with textured walls: LIO drifts in the corridor, LVIO does not | grandtour | [EXP-004](../experiments/EXP-004-robust-photometric.md), [EXP-012](../experiments/EXP-012-image-quality-gate.md) | ⬜ |
| G03 | Evaluation done right: frames, lever arms, alignment, ATE/RTE, noise floors | one trajectory, three alignments: how frames change ATE | nclt, grandtour | [EXP-000](../experiments/EXP-000-baselines-and-noise-floor.md) | ⬜ |

### Part X · Capstone: real systems and the ablation study  <sub>(SAD ch. –)</sub>

| # | Chapter | Synthetic scene | Real data | Experiments | Status |
|---|---|---|---|---|---|
| X01 | Anatomy of lightning-lm: the book's ideas in a production LIO | – | – | [EXP-019](../experiments/EXP-019-lightning-tuning-fairness.md) | ⬜ |
| X02 | Anatomy of SE(3)-LVIO: SE(3) IEKF, VoxelMap, photometric update, plane BA | – | – | [EXP-000](../experiments/EXP-000-baselines-and-noise-floor.md), [EXP-009](../experiments/EXP-009-se3-vs-so3xr3.md), [EXP-020](../experiments/EXP-020-map-structure-speed.md) | ⬜ |
| X03 | Running the ablation study: from spec to verdict | – | – | [EXP-000](../experiments/EXP-000-baselines-and-noise-floor.md), [EXP-001](../experiments/EXP-001-chi2-gate-sweep.md) | ⬜ |
| X04 | Design your own experiment | – | – | – | ⬜ |

🔗 = bridge chapter: not in the SAD book, needed for the capstone systems; always has an "On real data" step.
<!-- course:end curriculum -->

## How every chapter is built

| Section | What you get |
|---|---|
| What you will build | the modules and the one command to run (plus the book chapter it accompanies) |
| Intuition | the idea in plain words, before any symbol |
| The math | one equation per block, every symbol explained |
| Build it | step-by-step Python, each step with its printed output |
| See it | generated figures with "what to look at" captions |
| Break it | change one thing and watch it fail, with a number |
| Run it in C++ | the official SAD implementation on the official dataset (chapters with a book counterpart) |
| On real data | your Python code on SAD bags or GrandTour (always in 🔗 bridge chapters) |
| In the real systems | where the idea lives in lightning-lm and SE(3)-LVIO |
| Experiment hooks | the ablations that test it on GrandTour |
| Try it | predict-then-run exercises, answers folded |
| Next | the chapter that builds on this one |

> [!NOTE]
> The book's text and figures are not reproduced here. Each chapter links its book chapter for the full
> derivation, and builds the idea independently. Python timings teach **scaling** only. Absolute speed comes
> from the C++ labs and the experiments.
