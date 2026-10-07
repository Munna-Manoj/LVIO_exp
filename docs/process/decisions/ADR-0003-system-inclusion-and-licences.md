# ADR-0003 — Including the systems under test

- **Status:** Accepted (2026-10-07)

## Context
- SE(3)-LVIO (`url-kaist/se3-livom-comfort`) is GPL-2.0, and ablations need code changes in it.
- lightning-lm (`gaoxiang12/lightning-lm`) has **no licence**. All rights are reserved by default,
  so we may not redistribute its code, configs or documentation.
- This repository's own code (lvx, docs, tools) is MIT.

## Decision
- **SE(3)-LVIO:** fork it to `Munna-Manoj/se3-livom-comfort`, with every ablation on branch `lvio-exp`.
  - It is included as the git submodule `systems/se3-lvio`. The submodule is a reference, so no GPL code sits in this tree.
  - Each flag's default reproduces upstream behaviour.
- **lightning-lm:** fetched by `scripts/build_lightning.sh` at the pinned commit, outside the repo.
  - We track only our own files: the headless runner, the bag converter, the Containerfile, and
    override YAMLs that list just the keys we change.
  - The full config is assembled at run time from upstream plus our overrides.
- **Pins:** both are recorded in `systems/systems.yaml`. A pin change is its own commit and triggers EXP-000.

## Consequences
- `tools/check_tree.py` rejects any other file under `systems/lightning-lm/`.
- Ideas borrowed from lightning-lm (degeneracy projection, step limits, keyframe insertion) are
  **reimplemented** in the fork from the papers or our own understanding, never copied.
