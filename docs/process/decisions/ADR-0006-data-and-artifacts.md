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
| Viewer point clouds (decimated ≤ 1.5 M pts) | `docs/assets/experiments/<EXP>/viewer/` | yes, Git LFS, ≤ 8 MB |

- **Ground truth isn't committed.** It belongs to the dataset; evaluation reads it from `$LVX_DATA_ROOT`.
- **Dataset licence:** check the GrandTour terms before publishing derived maps (tracked in M2.2).
