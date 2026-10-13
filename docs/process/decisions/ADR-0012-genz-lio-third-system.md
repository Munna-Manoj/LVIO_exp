# ADR-0012 — GenZ-LIO as the third system, with ablations in both forks

- **Status:** Accepted (2026-10-12)

## Context
- The owner wants every study to cover three systems: SE(3)-LVIO, lightning-lm and GenZ-LIO.
- [GenZ-LIO](https://github.com/cocel-postech/genz-lio) (Lee, Lim et al., IEEE T-FR 2026, [arXiv:2603.16273](https://arxiv.org/abs/2603.16273)) was released in September 2026 under GPL-2.0.
  - It is a LiDAR–inertial odometry with three ideas of its own: a PID controller on the voxel size, combined point-to-plane and point-to-point residuals, and a voxel-pruned correspondence search.
  - Its filter state is SO(3)×R³ (the IKFoM toolkit FAST-LIO uses), a natural counterpart to SE(3)-LVIO's coupled SE(3) state (EXP-009).
  - It has a Python API, so it can read a mission's `comfort_offline/` folder directly; no bag conversion is needed.
- lightning-lm has no licence (ADR-0003), so a modified copy of it can never be published.

## Decision
- **Inclusion:** GenZ-LIO is included the way SE(3)-LVIO is (ADR-0003).
  - It is forked to `Munna-Manoj/genz-lio`, and everything we add goes on branch `lvio-exp`.
  - The fork is the git submodule `systems/genz-lio`, pinned in `systems/systems.yaml`.
  - The fork holds our runner (`lvio_exp/run_comfort.py`), the GrandTour config and the Containerfile, so no GPL code sits in this tree.
  - The image is built from the submodule at its pin.
- **Baseline config `genz_stock`:** upstream's `default/hesai.yaml` with only the platform keys changed: 4 threads, a 0.6 m blind range, and the extrinsic from `calib.json`.
  - Tuning beyond that is its own experiment, like EXP-019 for lightning-lm.
- **Noise floor:** EXP-000 is concluded and cannot grow, so a GenZ-LIO noise experiment measures its run-to-run σ and coverage on the dev missions.
  - That was EXP-021. It was concluded before we found that its runs lacked the per-mission IMU time offset; it is superseded by **EXP-022** (2026-10-12), which is the noise experiment used for GenZ-LIO.
  - No other experiment may run GenZ-LIO variants before EXP-022 is concluded `adopt`.
- **Ablations run in both forks:**
  - Every ablation experiment implements its idea in SE(3)-LVIO and, where the idea applies, in GenZ-LIO.
  - Each system gets its own variant against its own baseline (e.g. `gate_se3`, `gate_genz`), so a variant still differs from its baseline in one change (law 4).
  - Where an idea does not apply to GenZ-LIO (for example the camera update, P5), the spec says so.
- **lightning-lm stays reference-only:** it runs unmodified in the cross-system experiments (EXP-000, EXP-017, EXP-018, EXP-019) and appears as a reference in the others.
- **Specs:** `system:` may be `all` (the three systems) besides a single system or `both`.

## Consequences
- The planned specs EXP-001 … EXP-020 are reworked to add GenZ-LIO variants before they are frozen. They are not frozen yet, so this breaks no lock.
- Host time per ablation experiment roughly doubles (GenZ-LIO takes about 2 min per ARC-6 run on 4 cores).
- Course chapters name GenZ-LIO in "In the real systems" wherever it does the thing the chapter teaches.
- A pin change of GenZ-LIO is its own commit and reruns its noise experiment (now EXP-022), as a pin change of the others reruns EXP-000.

## Alternatives considered
- **Pinned pip wheel (`genz-lio==0.1.0`):** simpler, but not tied to a source commit, and there is nowhere to add ablation flags.
- **GenZ-LIO as a reference only, like lightning-lm:** cheaper, but the owner wants the ideas tested in GenZ-LIO too, and its licence allows it.

## Addendum (2026-10-12): two-system ablations

- **Pairing.** A GenZ-LIO arm runs `baseline: genz_stock` and names its **`reference`**: a plain swap arm `genz` in the same spec (GenZ-LIO stock, compared with `baseline` like EXP-000's cross-system rows).
  - Against its reference, a GenZ-LIO arm changes one thing (law 4); `lvx/spec.py` checks this.
  - `lvx eval` computes Δ against the reference, and takes σ from the arm's own baseline config (EXP-022 for `genz_stock`).
- **Flags in the GenZ-LIO fork** go in a config section `lvio_exp:` of `lvio_exp/grandtour_xt32.yaml`, each defaulting to upstream behaviour. Overrides are written `lvio_exp.<flag>`. A flag is added to the fork before its experiment is frozen.
- **Verdict.** The frozen decision rule is applied to each system separately, against its own reference and noise floor.
  - The experiment's verdict is `adopt` if the rule adopts for both systems, `reject` if it rejects for both, and `inconclusive` otherwise.
  - The TL;DR always gives the outcome per system.
- **Where GenZ-LIO does not apply:**
  - EXP-004, EXP-012 and EXP-013 change the photometric camera update, and GenZ-LIO is LiDAR-only.
  - EXP-014 and EXP-015 work on the backend, and GenZ-LIO has none.
  - EXP-020 is about SE(3)-LVIO's own map internals.
  - These stay `system: se3-lvio`.
- **GenZ-LIO's ideas in SE(3)-LVIO.** Each idea is tested in both systems: added to SE(3)-LVIO (reimplemented from the paper, since GenZ-LIO is GPL-2.0), and switched off in GenZ-LIO.
  - EXP-023: the scale-aware point budget (a setpoint that grows with the scene's scale, tracked by a PID on the voxel size).
  - EXP-024: point-to-point residuals for points without a plane (the hybrid-metric update).
  - EXP-025: thinning of the point-to-point candidates. It runs in GenZ-LIO only, because SE(3)-LVIO has no such candidates unless EXP-024 adopts the fallback.
- **GenZ-LIO tuning fairness:** EXP-026, alongside EXP-019 for lightning-lm.
