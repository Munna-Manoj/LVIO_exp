# 3D viewer (planned, M2.2)

A static three.js page deployed at `/viewer/`, the 3D companion of every experiment report.

| Requirement | Detail |
|---|---|
| Input | `docs/assets/experiments/<EXP>/viewer/<mission>.json` (trajectories: GT prism, baseline, variants) + `<mission>.bin` (float32 xyz + uint8 intensity, ≤ 1.5 M points, Git LFS) |
| Produced by | `lvx viewer <EXP>` (to be added), from repeat-1 runs; same colours as `lvx/plotstyle.py` |
| Deep link | `/viewer/?exp=EXP-001&mission=arc-6` |
| Controls | orbit, toggle each trajectory, colour points by height / intensity, error-coloured trajectory |
| Budget | first paint < 3 s on a laptop; no server |

Stack: Vite + React + three.js (@react-three/fiber), the same stack as the DS-MSP studio.
