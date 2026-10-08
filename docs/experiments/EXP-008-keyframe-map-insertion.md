# EXP-008 — Should the map be updated every scan or only at keyframes?

**TL;DR:** TODO one sentence with the answer and its number (after the verdict).

<!-- lvx:begin status -->
**Status:** 🗒️ planned · **Phase:** P3 (Map quality) · **System:** `se3-lvio` · **Depends on:** EXP-000
<!-- lvx:end status -->

## Question & hypothesis

<!-- lvx:begin hypothesis -->
| | |
|---|---|
| **Question** | Does lightning-lm-style keyframe-only map insertion (1 m / 10°) change ATE and runtime for SE(3)-LVIO? |
| **Hypothesis** | Per-scan insertion gives a denser reference but also inserts transient objects and costs time; keyframe insertion trades density for speed. |
| **Prediction** | Slightly worse ATE (sparser planes), lower ms_p95. |
| **Falsified if** | better ATE beyond noise (would mean per-scan insertion pollutes the map). |
| **Decision rule** | adopt if the mean primary metric over the missions improves by more than 2σ run-to-run noise on at least 2/3 of the missions, no mission gets worse beyond 2σ, and ms_p95 grows by less than 10 %; reject if it is worse beyond 2σ on any mission; otherwise inconclusive. |

<sub>Fields above are draft, not frozen yet (`spec.lock`).</sub>
<!-- lvx:end hypothesis -->

## Setup

<!-- lvx:begin setup -->
| Variant | The one change |
|---|---|
| `baseline` | se3lvio_S8 as is |
| `kf_insert` | insert scans into the voxel map only at keyframes (1 m / 10°) |

- **Missions:** arc-6, eig-2, snow-3 (`{"set": "dev"}`)
- **Repeats:** 3 per variant × mission
- **Host:** `reference` (configs/hosts/reference.yaml)
- **Metrics:** primary `ate_rmse_cm`, secondary `ate_max_cm`, `ms_p95`, `rss_mb`
- **Commits:** recorded per run once runs exist
<!-- lvx:end setup -->

## Results

<!-- lvx:begin results -->
> [!NOTE]
> Not run yet (status `planned`). Numbers appear here after `lvx eval EXP-008`.
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
lvx run EXP-008 --host reference     # every variant × mission × repeat, on the reference host
lvx eval EXP-008                  # runs.csv + summary.json
lvx figures EXP-008
lvx report EXP-008
```
<!-- lvx:end reproduce -->
