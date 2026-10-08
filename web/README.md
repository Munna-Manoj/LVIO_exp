# 3D viewer (M2.2)

The viewer is one static page, [`docs/viewer/index.html`](../docs/viewer/index.html), published with the site at
`/viewer/`. It is the 3D companion of every experiment report.

| | Detail |
|---|---|
| Input | `docs/assets/experiments/<EXP>/viewer/`: `index.json` (missions), `<mission>.json` (trajectories in the GT frame), `<mission>.bin` (map, uint16 x y z, ≤ 300k points, ≤ 2 MB: no Git LFS) |
| Produced by | `lvx viewer <EXP>` on the host ([`lvx/viewer.py`](../lvx/viewer.py)), from the repeat-1 runs; colours from `lvx/plotstyle.py` |
| Also writes | `<mission>_map.png` (top view, shown in the report on GitHub) and, on request, `<mission>.gif` (README) |
| Deep link | `/viewer/?exp=EXP-000&mission=arc-6` |
| Controls | orbit, toggle each trajectory, height cut (hides the ceiling), point size |
| Stack | three.js 0.160 from jsDelivr through an import map: no build step, no server |

This folder holds only this README. The page lives under `docs/`, so MkDocs publishes it unchanged.
