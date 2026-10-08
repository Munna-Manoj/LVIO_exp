# Licensing

| Part | Licence |
|---|---|
| This repository: `lvx/`, `tools/`, `scripts/`, `tests/`, `docs/`, `configs/`, `web/`, `systems/lightning-lm/*` (our files) | MIT ([LICENSE](LICENSE)) |
| `systems/se3-lvio` (git submodule, not part of this tree) | GPL-2.0, its own repository |
| lightning-lm upstream | no licence; never redistributed, fetched at build time (ADR-0003) |
| SAD code (`slam_in_autonomous_driving`) | MIT; pinned, built outside the repo, never vendored (ADR-0008) |
| SAD book text and figures | not reproduced; chapters are linked only (ADR-0008) |
| SAD datasets (NCLT, UrbanLoco, UTBM, WXB, 2dmapping, AVIA) | each dataset's own terms; never committed |
| GrandTour data and anything derived from it (maps, GT) | MIT (HuggingFace release); cite Frey, Tuna et al., arXiv:2602.18164. Derived viewer maps are published with that attribution; GT is not committed (ADR-0006) |
