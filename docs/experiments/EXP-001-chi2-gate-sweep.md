# EXP-001 — How wide should the residual gate be?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P1 (Outliers and robustness) · **System:** `se3-lvio` + `genz-lio` + `lightning-lm` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
**Terms used on this page**

| Term | Meaning |
|---|---|
| **ATE** | Absolute trajectory error: the root-mean-square distance between the estimated trajectory and the ground-truth trajectory, in centimetres, after the two are aligned. Lower is better. |
| **scan time (ms_p95)** | The time a system needs to process one LiDAR scan, in milliseconds. `ms_p95` is the 95th percentile over a mission: 95 % of the scans take less than this. |
| **noise floor** | The smallest ATE difference that counts as a real effect: 2 × σ, where σ is the standard deviation of ATE between identical runs of that system's stock config (EXP-000 for SE(3)-LVIO and lightning-lm, EXP-022 for GenZ-LIO). It is never less than 0.01 cm. |
| **variant** | One configuration that is run. Each variant differs from the variant it is compared with in exactly one change. |
| **dev missions** | The three missions used to decide experiments: ARC-6 (indoor, with smoke), EIG-2 (a glacier climb, outdoor) and SNOW-3 (a snow field, outdoor). The test missions are kept for final reports. |
| **`baseline` (S8)** | SE(3)-LVIO's stock config `se3lvio_S8`: one LiDAR (the Hesai XT32) and the IMU, no camera, no backend. |
| **`genz`** | GenZ-LIO's stock config `genz_stock`: upstream's Hesai settings, with only the sensor calibration and the 4-core limit set. |
| **`lightning`** | lightning-lm's config `lightning_indoor`: upstream's settings with 0.2 m grids. It is the better of lightning-lm's two configs on ARC-6 in EXP-000 (1.41 cm against 1.64 cm). |
| **lightning-lm on the field missions** | Both lightning-lm configs lose track on EIG-2 and SNOW-3 in EXP-000 (`lightning`: 294 cm and 41 cm). A lightning-lm variant is therefore judged on ARC-6 only. Its EIG-2 and SNOW-3 numbers are still reported. |
| **σ (in a limit)** | The expected spread of a point's distance to its plane, computed from the point's and the plane's uncertainty. A 3σ limit drops a point more than 3 such spreads from its plane. |
| **lightning-lm's bound** | lightning-lm has no σ. It drops a point whose distance to the plane is more than √(range) / 9, with the range in metres. Its variants scale that bound. |

**Which systems take part**

| System | Takes part | How, or why not |
|---|---|---|
| SE(3)-LVIO | yes | Its 3σ point-to-plane limit is swept: 2σ, 2.5σ, 4σ, 5σ. |
| GenZ-LIO | yes | Its point-to-plane limit `mapping.sigma_num` is swept with the same values. |
| lightning-lm | yes | Its fixed bound is scaled by the same ratios (0.67, 0.83, 1.33, 1.67). |

| | |
|---|---|
| **Question** | Each system drops a LiDAR point from the scan update when the point is too far from its matched plane. Does a tighter or a looser limit than the stock one change ATE? |
| **Hypothesis** | The IMU predicts the pose well enough that the stock limit already separates good matches from bad ones. A tighter limit drops good matches, so ATE gets worse. A looser limit lets in points on smoke and clutter, so ATE gets slightly worse on ARC-6. |
| **Prediction** | SE(3)-LVIO and GenZ-LIO: ATE changes by less than the noise floor at 2.5σ and 4σ. ATE is worse at 2σ, and slightly worse at 5σ on ARC-6. GenZ-LIO loses less at 2σ than SE(3)-LVIO, because GenZ-LIO gives a point that fails the plane limit a point-to-point residual instead of dropping it. lightning-lm, on ARC-6: the same pattern, with the bound scaled by the same factors. |
| **Falsified if** | In SE(3)-LVIO or GenZ-LIO, a limit other than the stock one improves ATE by more than the noise floor on at least two of the three dev missions. |
| **Decision rule** | For each system separately, compare every limit with the stock limit, mission by mission. A limit qualifies if it is better than the stock limit (ATE lower by more than the noise floor) on at least two of the three dev missions, worse on none, and its ms_p95 is less than 10 % higher. For lightning-lm only ARC-6 is judged, so a lightning-lm limit qualifies if it is better on ARC-6. A system adopts the qualifying limit with the lowest mean ATE. A system keeps its stock limit (reject) if every other limit is worse on at least one judged mission; otherwise the result for that system is inconclusive. Verdict: adopt if every system adopts a new limit, reject if every system keeps its stock limit, and inconclusive otherwise. |

<sub>The five fields in this table are a draft; they are locked when the experiment is approved (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
Each variant differs from the variant it is compared with in exactly one change. A variant marked – runs another system's stock config, and the variants of that system are compared with it.

| Variant | System | Compared with | What this variant changes |
|---|---|---|---|
| `baseline` | SE(3)-LVIO | – | the stock config `se3lvio_S8`, unchanged |
| `gate_2p0` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: limit 2.0σ (stock 3.0σ) |
| `gate_2p5` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: limit 2.5σ (stock 3.0σ) |
| `gate_4p0` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: limit 4.0σ (stock 3.0σ) |
| `gate_5p0` | SE(3)-LVIO | `baseline` | SE(3)-LVIO: limit 5.0σ (stock 3.0σ) |
| `genz` | GenZ-LIO | – | GenZ-LIO's stock config. The GenZ-LIO variants are compared with this one. |
| `genz_gate_2p0` | GenZ-LIO | `genz` | GenZ-LIO: plane limit 2.0σ (stock 3.0σ) |
| `genz_gate_2p5` | GenZ-LIO | `genz` | GenZ-LIO: plane limit 2.5σ (stock 3.0σ) |
| `genz_gate_4p0` | GenZ-LIO | `genz` | GenZ-LIO: plane limit 4.0σ (stock 3.0σ) |
| `genz_gate_5p0` | GenZ-LIO | `genz` | GenZ-LIO: plane limit 5.0σ (stock 3.0σ) |
| `lightning` | lightning-lm | – | lightning-lm's indoor config. The lightning-lm variants are compared with this one. |
| `lightning_bound_0p67` | lightning-lm | `lightning` | lightning-lm: residual bound × 0.67 (the same ratio as 2σσ against 3σ) |
| `lightning_bound_0p83` | lightning-lm | `lightning` | lightning-lm: residual bound × 0.83 (the same ratio as 2.5σσ against 3σ) |
| `lightning_bound_1p33` | lightning-lm | `lightning` | lightning-lm: residual bound × 1.33 (the same ratio as 4σσ against 3σ) |
| `lightning_bound_1p67` | lightning-lm | `lightning` | lightning-lm: residual bound × 1.67 (the same ratio as 5σσ against 3σ) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `inliers_mean`, `ms_p95`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-001`.
<!-- lvx:end results -->

TODO up to 5 observations, each pointing at a table cell or figure.

## Discussion

TODO why it happened; link the theory in docs/explain/.

## Verdict

TODO adopt / reject / inconclusive, citing the decision rule.

## Threats to validity

TODO what could make this conclusion wrong.

## Failures

TODO failed or dirty runs and why (or "none").

## Reproduce

<!-- lvx:begin reproduce -->
```bash
lvx run EXP-001 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-001                  # runs.csv + summary.json
lvx figures EXP-001
lvx viewer EXP-001                # on the host: map + trajectories for the 3D viewer
lvx report EXP-001
```
<!-- lvx:end reproduce -->
