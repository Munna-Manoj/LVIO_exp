# lightning-lm (our files only)

lightning-lm has no licence, so nothing from upstream is tracked here. Our code changes to lightning-lm live in
a private fork (`Munna-Manoj/lightning-lm-lvio`, branch `lvio-exp`), which is never published
([ADR-0013](../../docs/process/decisions/ADR-0013-lightning-lm-private-fork.md)).

| File | Purpose |
|---|---|
| `runner/run_lio_tum.cc` | headless LIO frontend: ROS 2 bag → TUM poses + per-scan `timing.csv` |
| `offline_to_ros2bag.py` | GrandTour `comfort_offline` → ROS 2 bag (`/imu`, `/points`) |
| `Containerfile` | ROS 2 Humble build image (Pangolin from the upstream zip at build time) |
| `overrides/*.yaml` | only the config keys we change, merged onto upstream `default_robosense.yaml` by lvx |

Build: `bash scripts/build_lightning.sh`. It clones the private fork at the commit pinned in `systems/systems.yaml`.
A host that cannot reach GitHub sets `systems.lightning-lm.source` in `lvx.local.yaml` to a local mirror of the fork.
