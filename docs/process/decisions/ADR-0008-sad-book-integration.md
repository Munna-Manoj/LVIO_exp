# ADR-0008 — The SAD book as the course backbone, the real systems as the capstone

- **Status:** Accepted (2026-10-07). Supersedes the F/I chapter numbering of ADR-0007; the rest of
  ADR-0007 stands.

## Context
- *SLAM in Autonomous Driving* (SAD, Gao Xiang et al.) already teaches inertial navigation, point
  clouds, 2D/3D LiDAR SLAM, LIO, mapping and localisation, in a gradual order.
  - Its code is MIT; its datasets are published.
  - lightning-lm is the same author's production LIO, so the course leads naturally into it.
- A separate F/I numbering would duplicate the book's structure and confuse readers who use both.

## Decision
- **Book order:** the course follows the book's chapter order.
  - Parts A–F follow SAD chapters 2–10 (B05 robust estimation is added).
  - Part G goes beyond the book: photometric alignment, LVIO, evaluation.
  - Part X is the capstone: lightning-lm, SE(3)-LVIO, the ablation study, your own experiment.
- **Three tracks per chapter:**
  - **Build it** (our Python, synthetic, independent of the book's code);
  - **Run it in C++** (`lvx lab run`, the official SAD apps on the official datasets, in a sandbox, with manifests);
  - **Test it at scale** (experiment hooks).
- **Single source:** `course/curriculum.yaml` holds parts, chapters, dependencies, SAD apps, labs and status.
  `configs/datasets.yaml` holds every dataset with its official link.
- **Licensing:**
  - The SAD code is pinned in `systems/systems.yaml` and built outside the repo.
  - The book's text and figures are never reproduced, only linked. Pages derive ideas in their own words.

## Consequences
- **Two equal paths:** readers can follow the book and this course side by side. Chapter B01 maps to
  SAD chapter 3, and so on.
- **Labs are trackable:** each has a recorded run (commit, image, wall time, exit code).
  They are reproducible on any host with the SAD container.
- **Lab hygiene:** SAD apps write into `./data/`, so labs always run in a sandbox and never in the SAD tree.

## Addendum (2026-10-07): bridge chapters

- **What they are:** topics the book does not cover, but SE(3)-LVIO and lightning-lm rely on, become
  **bridge chapters** `I01…` (`kind: bridge`). Each is placed inside the book part where the reader
  first needs it:
  - I01 real IMUs and Allan variance (after B01)
  - I02 time offsets and extrinsics (after B02)
  - I03 degeneracy (after D03)
  - I04 map structures in the loop, and I05 multi-LiDAR fusion (after E02)
  - I06 online smoothing backend, and I07 dynamic objects and map hygiene (after F02)
- **Real data is required.** Bridges always have an "On real data" step on the SAD datasets and/or
  GrandTour, read in Python (`rosbags`, `comfort_offline`).
- **Why not fold them into book chapters?** Then the book-aligned chapters would stop matching the
  book. Readers using both would lose the one-to-one mapping.
