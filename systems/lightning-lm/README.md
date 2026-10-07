# lightning-lm (our files only)

lightning-lm has no licence, so nothing from upstream is tracked here
([ADR-0003](../../docs/process/decisions/ADR-0003-system-inclusion-and-licences.md)).

| File | Purpose |
|---|---|
| `runner/run_lio_tum.cc` | headless LIO frontend: ROS 2 bag → TUM poses + per-scan `timing.csv` |
| `offline_to_ros2bag.py` | GrandTour `comfort_offline` → ROS 2 bag (`/imu`, `/points`) |
| `Containerfile` | ROS 2 Humble build image (Pangolin from the upstream zip at build time) |
| `overrides/*.yaml` | only the config keys we change, merged onto upstream `default_robosense.yaml` by lvx |

Build: `bash scripts/build_lightning.sh` (fetches upstream at the pinned commit in `systems/systems.yaml`).
