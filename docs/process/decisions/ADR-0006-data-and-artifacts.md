# ADR-0006 — Data and artefacts

- **Status:** Accepted (2026-10-07)

## Decision
| Artefact | Where | Tracked? |
|---|---|---|
| GrandTour missions, bags, images | `$LVX_DATA_ROOT` on the host | no |
| Full run outputs (logs, all repeats) | `$LVX_RUN_ROOT/<EXP>/…` (append-only) | no |
| `runs.csv`, `summary.json`, manifests | `experiments/<EXP>/results/` | yes |
| Repeat-1 estimates (`.tum.gz`) | `experiments/<EXP>/results/traj/` | yes (small) |
| Figures | `docs/assets/experiments/<EXP>/` | yes, ≤ 2 MB each |
| Viewer maps (≤ 300k pts, uint16) + trajectories | `docs/assets/experiments/<EXP>/viewer/` | yes, ≤ 2 MB each (no Git LFS; changed 2026-10-08) |

- **Ground truth isn't committed.** It belongs to the dataset; evaluation reads it from `$LVX_DATA_ROOT`.
- **Dataset licence (checked 2026-10-08):** the GrandTour HuggingFace release is MIT-licensed, and its README asks
  that the dataset paper be cited (Frey, Tuna et al., arXiv:2602.18164). Derived maps may be published with that
  attribution; the viewer page and every report's Maps section carry it.
