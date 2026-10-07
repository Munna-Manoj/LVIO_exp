# CLAUDE.md — operating rules for LVIO_exp

This repository has two tracks that feed each other:
1. **The study:** a controlled ablation study of two LiDAR-inertial(-visual) odometry systems,
   **SE(3)-LVIO** and **lightning-lm**, on GrandTour / COMFORT data.
2. **The course:** a hands-on course that teaches LiDAR-visual-inertial SLAM one building block at a
   time.
   - It follows the book *SLAM in Autonomous Driving* (SAD, parts A–F) and goes beyond it (part G:
     camera, LVIO, evaluation).
   - It ends in a **capstone** (part X): lightning-lm, SE(3)-LVIO, and this ablation study.
   - Each chapter has three tracks: Build it (Python, synthetic), Run it in C++ (official SAD code on the
     official datasets), and Test it at scale (the ablations).

It is also a public portfolio. Every rule below exists so that it never turns into a pile of one-off
scripts and unexplained numbers.

These rules are **mandatory**. When a rule conflicts with a request, say so and ask before you break it.
"Faster" or "just this once" is not a reason to skip a rule.

Read these before your first change in a session:
1. This file.
2. [`docs/process/EXPERIMENT_PROTOCOL.md`](docs/process/EXPERIMENT_PROTOCOL.md): the lifecycle, the IDs, the decision rule.
3. [`docs/process/WRITING_GUIDE.md`](docs/process/WRITING_GUIDE.md): how every page is written.
4. [`ROADMAP.md`](ROADMAP.md): what is in progress right now.
5. For course work: §11 below and [`docs/learn/README.md`](docs/learn/README.md) (the curriculum).

---

## 0. The five laws

1. **No number without a run.** Every number in a README, doc page, report, commit message or chat
   answer about results comes from a generated results file:
   - `experiments/<EXP>/results/`, written by `lvx`, with a run manifest behind it; or
   - `course/chapters/<ID>/results/`, written by that chapter's `run.py`.

   If no such file exists, the number does not exist. Write "not measured yet" instead.
2. **No run without a spec.** Nothing is executed for a result unless an experiment spec
   (`experiments/EXP-NNN-<slug>/spec.yaml`) exists and is `approved` (frozen). Exploratory
   poking goes in `scratch/` (gitignored) and never gets reported.
3. **The hypothesis is written before the data.** Run `lvx exp freeze` to record the hash of the
   question, hypothesis, prediction and decision rule. Never edit those fields after freezing.
   If the plan must change, create a new experiment that `supersedes` the old one.
4. **One change per variant.** A variant differs from its baseline in exactly one flag or one patch.
   A second change makes it a second variant.
5. **Negative results are results.** A frozen experiment ends `concluded` (with a verdict, even
   "no effect") or `abandoned` (with a reason). Never delete it, rename it, or rerun it until it
   says what you hoped.

---

## 1. Repository map (where things go)

```
LVIO_exp/
├─ CLAUDE.md  README.md  ROADMAP.md  CONTRIBUTING.md  LICENSE  LICENSING.md
├─ lvx/                     Python package + CLI (`lvx`): specs, runs, eval, figures, reports
├─ tools/                   governance checkers run in CI (check_*.py)
├─ scripts/                 build + figure scripts (build_lightning.sh, make_*_figures.py)
├─ .claude/commands/        /exp-status, /exp-new, /exp-run, /exp-conclude (use them)
├─ tests/                   pytest for lvx, the checkers, and every course chapter (tests/course/)
├─ course/
│  ├─ curriculum.yaml       THE curriculum: parts, chapters, SAD chapter/apps, labs, experiments, status
│  ├─ lvio_course/          the course's NumPy building blocks (so3, imu, maps, eskf, graph, …); grows chapter by chapter
│  └─ chapters/<ID>-<slug>/ run.py, results/{run.txt,metrics.json}, results/labs/<lab>/{manifest.json,log_tail.txt}
├─ configs/
│  ├─ datasets.yaml         every dataset (SAD sets, GrandTour): official links, size, local path, users
│  ├─ missions.yaml         GrandTour mission registry + dev/test split (the only place missions are defined)
│  ├─ stress.yaml           data-side degradation profiles (P6)
│  ├─ baselines/            frozen baseline configs, one per system setting
│  └─ hosts/                host profiles (CPU, cores, container runtime); no personal paths
├─ systems/
│  ├─ systems.yaml          pinned upstream repos + commits + licences
│  ├─ se3-lvio/             git submodule (fork branch `lvio-exp`), all ablation flags live there
│                           (SAD is pinned in systems.yaml and built outside the repo: $LVX_SAD_ROOT)
│  └─ lightning-lm/         OUR runner, converter, Containerfile, config overrides only
├─ experiments/
│  ├─ _template/            spec.yaml template
│  ├─ registry.md           generated index of all experiments (never hand-edit)
│  └─ EXP-NNN-<slug>/
│     ├─ spec.yaml          pre-registered design (frozen fields + lock hash)
│     ├─ spec.lock          written by `lvx exp freeze`
│     └─ results/           written ONLY by lvx: runs.csv, summary.json, manifests/, traj/
├─ docs/                    MkDocs Material site (also readable on GitHub)
│  ├─ index.md
│  ├─ learn/<ID>-<slug>.md                       course chapters (A01 … X04, see course/curriculum.yaml)
│  ├─ how-to/  explain/  reference/              Diátaxis sections
│  ├─ assets/learn/<ID>/                         chapter figures (generated by the chapter's run.py)
│  ├─ experiments/EXP-NNN-<slug>.md              the experiment REPORT (one per experiment)
│  ├─ assets/experiments/EXP-NNN/                generated figures + viewer assets
│  └─ process/              protocol, writing guide, DoD, ADRs (contributor-facing, not published)
├─ web/                     three.js point-cloud / trajectory viewer, deployed at /viewer/
└─ scratch/                 gitignored; anything exploratory
```

Rules:
- **Don't add new top-level files or directories** without an ADR.
  `tools/check_tree.py` enforces an allowlist.
- **Never commit:** raw data, bags, zarr, full-resolution point clouds, binaries, container images, or
  anything machine-specific (see §12). Tracked files name datasets, systems and host profiles **by name only**.
- **Size limits:** each tracked file ≤ 2 MB. A viewer point cloud is ≤ 8 MB (stored with Git LFS),
  decimated to ≤ 1.5 M points. GIFs ≤ 6 MB.
- **lightning-lm has no licence.** Never copy its source, configs or docs into this repo. We commit
  only our own runner, our converter, and *override* YAMLs that list just the keys we change. The
  build fetches upstream at the pinned commit (ADR-0003).
- **SE(3)-LVIO is GPL-2.0.** Code changes go into the fork submodule (`systems/se3-lvio`, branch
  `lvio-exp`), never into a copy in this repo. Each ablation is one config flag whose default
  reproduces the baseline bit-for-bit (or within the noise floor; see §3).

---

## 2. Experiment lifecycle (strict)

```
planned ──approve+freeze──▶ approved ──first run──▶ running ──all runs+eval──▶ analysed ──verdict──▶ concluded
   └──────────────────────────────────────────── abandoned (reason required) ◀───────────┘
```

| Step | Command | What must be true before you move on |
|---|---|---|
| Propose | `lvx exp new <slug> --phase P1` | Spec filled in: question, hypothesis, prediction, falsification, variants, missions, repeats, metrics, decision rule. `status: planned`. |
| Approve | `lvx exp freeze EXP-NNN` | The **user** approved the spec in chat or in a PR. Freezing writes `spec.lock`. Never freeze without explicit user approval. |
| Implement | commits in the `systems/se3-lvio` fork | Flag added, default = baseline, unit/smoke test passes, baseline still reproduces (§3). |
| Run | `lvx run EXP-NNN [--variant v] [--mission m]` | Writes one manifest per run. Never run a variant or mission that the spec doesn't list. |
| Evaluate | `lvx eval EXP-NNN` | `runs.csv` + `summary.json`. Failed runs stay in the table as `failed`, never silently dropped. |
| Figures | `lvx figures EXP-NNN` | The standard figure set (§5), generated, never hand-made. |
| Report | `lvx report EXP-NNN` | Regenerates the `lvx:` blocks in the report. Then a human-style Discussion + Verdict is written by hand. |
| Conclude | `lvx exp conclude EXP-NNN --verdict {adopt,reject,inconclusive}` | The verdict follows the frozen decision rule, not intuition. |

- **Status is only changed by `lvx`**, never by editing `status:` by hand.
- **Check the lifecycle** with `python tools/check_experiments.py`. It runs in CI and must pass before
  every commit.
- **A failed or crashed run counts as data.** Record it in the report under
  "Failures"; never rerun until it passes.
- **To change the plan after freezing**, run `lvx exp new <slug> --supersedes EXP-NNN`. The old
  experiment is concluded `inconclusive` or abandoned, with a pointer to the new one.

---

## 3. Measurement rules (what makes a number trustworthy)

- **Evaluation protocol is fixed** (ADR-0002):
  - COMFORT/Codabench ATE (evo `point_distance`, rigid alignment, no scale, scorer `t_max` rule), in the **prism frame**.
  - Prism transform: `T_imu_prism` from `/tf_static`, plus the fixed lever-arm correction.
  - Per-mission IMU time offsets from `configs/missions.yaml`.
  - Both systems go through the same conversion and the same `lvx eval`.
- **Mission split:** tune on `dev`, report on `test` (ADR-0005). Never pick a variant by looking at
  `test` numbers. ARC-6 is in `dev`.
- **Noise floor first.** EXP-000 measures run-to-run spread per system and mission (≥5 repeats).
  An effect smaller than **2 × σ_noise** (the run-to-run spread) is "no effect", whatever its sign.
  `summary.json` carries this verdict per mission; reports quote it, never re-derive it by hand.
- **Repeats:** default 3 per (variant, mission), at least 5 for EXP-000.
- **Report the spread:**
  - mean ± std over repeats;
  - per-mission values, not only the average;
  - median and max as well as RMSE.
- **Timing is a first-class metric:**
  - ms/scan mean, p95, max and peak RSS, from the system's own timing output;
  - host profile recorded in the manifest;
  - core count pinned with `taskset`, using the cores from the host profile.
- **Fair comparison:** lightning-lm gets the same tuning budget on `dev` as SE(3)-LVIO had (EXP-019),
  so "ours is better" is never the result of an untuned baseline.
- **Every run manifest records:**
  - the commits of this repo and of the system, plus the dirty flag (dirty → the run is refused unless `--allow-dirty`, and then it is marked `dirty` and excluded from reports);
  - the config hash and the full resolved config;
  - the container image digest;
  - host profile, cores, command line, start and end time, exit code.

---

## 4. Reports (one per experiment, fixed shape)

The report lives at `docs/experiments/EXP-NNN-<slug>.md` and has **exactly these sections, in order**
(`tools/check_reports.py` checks them):

1. `# EXP-NNN — <question as a title>`, then a one-line answer (the TL;DR verdict, with the number).
2. `## Question & hypothesis`: generated from the frozen spec.
3. `## Setup`: generated: variants table (one change each), missions, repeats, host, commits.
4. `## Results`: generated tables + the standard figures, then **up to 5 bullet points** of
   observations, each pointing to a figure or table cell.
5. `## Discussion`: hand-written. *Why* did it happen? It ties back to the theory (link to
   `docs/explain/`).
6. `## Verdict`: adopt / reject / inconclusive, citing the frozen decision rule.
7. `## Threats to validity`: what could make this wrong (few missions, one host, tuning leakage…).
8. `## Failures`: failed and dirty runs, and why.
9. `## Reproduce`: the exact `lvx` commands.

Content between `<!-- lvx:begin NAME -->` and `<!-- lvx:end NAME -->` is **generated**.
- Never edit it by hand. `tools/check_reports.py` regenerates it and fails on drift.
- Hand-written text goes only outside these blocks.

The README results table and `experiments/registry.md` are generated the same way, by `lvx report --index`.

---

## 5. Visuals (the standard set)

Every concluded experiment has these, made by `lvx figures` with the shared style (`lvx/plotstyle.py`):

| Figure | File | Shows |
|---|---|---|
| Effect plot | `effect.png` | Δ ATE vs baseline per variant × mission, with the ±2σ_noise band shaded |
| Accuracy–cost | `pareto.png` | ATE vs ms/scan p95, one marker per variant, with the 10 Hz / 20 Hz budget lines |
| Error over time | `error_time.png` | baseline vs best variant on the most-affected mission |
| Trajectory overlay | `traj_top.png` | top-down: GT prism (black), baseline, variant |
| Viewer asset | `viewer/<mission>.json` + `.bin` | decimated map + trajectories, opened by `web/` |

- **Fixed colours:**
  - GT: black;
  - SE(3)-LVIO baseline: teal `#0f9d8a`;
  - lightning-lm: orange `#e8710a`;
  - variants: sequential palette from `plotstyle.VARIANT_COLORS`.
- **Fixed units:** cm for ATE, ms for time, MB for memory, m for maps.
- **Every figure has a caption** in the report that says what to look at ("the variant leaves the band
  only on SPX-2, where the robot climbs stairs").
- **3D views** go to the web viewer (`/viewer/?exp=EXP-NNN&mission=…`); the report embeds a static
  PNG render of the same view and links to it.
- **Diagrams** are Mermaid (they render on GitHub and MkDocs alike); no ASCII art and no
  screenshots of diagrams.

---

## 6. Documentation rules (for humans, not for us)

Read [`docs/process/WRITING_GUIDE.md`](docs/process/WRITING_GUIDE.md). In short:

- **Diátaxis:** each page is exactly one of Learn (tutorial), How-to, Explanation, Reference,
  Experiment report.
- **Lead with the point.** No paragraph over ~40 words. One idea per section.
- **Prove it with a number** that comes from a results file (law 1).
- **Formulas:** one relationship per display block, with each symbol named in prose right after.
- **Anything spatial gets a figure** (frames, planes, residuals, manifolds, trajectories).
- **Markdown must render on GitHub *and* MkDocs.**
  - Callouts: GitHub alert syntax `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`.
  - Diagrams: Mermaid. Maths: `$…$` / `$$…$$`.
  - No MkDocs-only syntax (`///`, `!!!`, `{* *}`) in `docs/experiments/` or in the README.
- **Tutorials** (`docs/learn/`) end with "Try it": a one-line change to predict, and then run.

---

## 7. Code rules

- **`lvx`** is Python ≥3.8, typed, `ruff`-clean, with tests in `tests/`. Every CLI command is
  idempotent and safe to re-run.
- **Configuration and paths:**
  - No hard-coded paths, hosts or mission lists in code. Missions come from `configs/missions.yaml`, systems from `systems/systems.yaml`, paths from env vars.
  - Config overrides use dotted keys (`lio.gate_sigma: 2.5`) resolved by `lvx`; the resolved config is stored in the manifest.
- **C++ changes** (in the fork):
  - Each flag is documented in the fork's config with its default and the experiment ID that introduced it.
  - Add no new dependencies without an ADR.
- **Commits:**
  - Conventional Commits with the experiment ID in the scope: `feat(EXP-003): GNC-TLS weights in IEKF update`, `docs(EXP-001): verdict`, `chore(lvx): …`.
  - One experiment per commit when it touches results.
- **Branches:**
  - `exp/EXP-NNN-<slug>` for experiment work, `infra/<topic>` for tooling, `docs/<topic>` for docs.
  - Never commit straight to `main`; merge via a PR whose template is the Definition of Done.

---

## 8. Before you say "done"

Run, and paste the summary lines of:

```bash
ruff check lvx tools tests
pytest -q
python tools/check_tree.py
python tools/check_experiments.py
python tools/check_reports.py
python tools/sync_course.py --check
mkdocs build --strict        # when docs changed
```

Then go through [`docs/process/DEFINITION_OF_DONE.md`](docs/process/DEFINITION_OF_DONE.md).
- If any check fails, the task is not done. Say so, with the output.
- If you skipped a step (e.g. a run that needs the server), say which one and why.

## 9. Working with the compute host

- **Runs happen on the machine that plays host profile `reference`** (`configs/hosts/reference.yaml`:
  hardware only). How to reach it (ssh alias, checkout) is in the git-ignored `lvx.local.yaml`; never write
  it into a tracked file, a commit message or a report.
  - That uses `ssh` + `podman`; no Docker, no root.
  - Long jobs run in the background with a log under `$LVX_RUN_ROOT/<EXP>/logs/`. Never in an interactive shell you then abandon.
- **Never delete or overwrite** anything under `$LVX_DATA_ROOT` or someone else's run directory.
  Run outputs are append-only: a rerun gets a new repeat index, never the same directory.
- **Pushing:**
  - Don't push to GitHub, open PRs or publish pages without the user's go-ahead in the current conversation.
  - Committing locally is fine.

## 10. Track the work

- `ROADMAP.md` is the single plan: milestones (M*) and experiments (EXP-*), each with a status.
- Update it in the same commit as the work.
- At the start of a session, read `ROADMAP.md` and `experiments/registry.md` and say which item you
  are working on.
- Don't start an item whose dependencies (the `depends_on` field in its spec) aren't concluded.

## 11. Course rules (course/ + docs/learn/)

The course is held to the same standard as the study. A chapter is a **tested program with a page**,
not an essay.

**Structure**
- **`course/curriculum.yaml` is the single source** for parts, chapters, order, dependencies, SAD
  chapter and apps, labs, linked experiments and status.
  - The tables in `docs/learn/README.md` are generated from it.
  - A new chapter starts as a row here, plus a row in ROADMAP.md. Never as a file first.
- **Parts:**
  - A–F follow the SAD book chapters 2–10, with B05 robust estimation added.
  - G goes beyond the book: photometric alignment, LVIO, evaluation.
  - X is the capstone: anatomy of lightning-lm, anatomy of SE(3)-LVIO, running the ablation study, your own experiment.
- **Chapter IDs** are `<part><nn>` (B01, C02, X03). A chapter may depend only on **earlier** chapters,
  and `tools/sync_course.py --check` enforces the order.
- **Bridge chapters (`I01`, `I02`, …, `kind: bridge`)** cover what the SAD book does not, but the
  capstone systems depend on:
  - real IMU noise / Allan variance;
  - time offsets and extrinsics;
  - degeneracy;
  - map structures inside the LIO loop;
  - multi-LiDAR fusion;
  - online smoothing backends;
  - dynamic objects and map hygiene.

  Rules for bridges:
  - **Placement:** a bridge sits in the curriculum list right where it is needed, inside a book part.
  - **IDs:** I-numbers run in course order, and a new one takes the next free number. Never renumber
    existing chapters, because links and results depend on the IDs.
  - **Before adding a topic as a bridge,** check that no SAD chapter covers it.
  - **Real data is required.** A bridge must list `datasets` (SAD sets and/or `grandtour`) and has a
    required `## On real data` section.
  - **Real data is read in Python** with `rosbags` (SAD bags, no ROS) or from the GrandTour
    `comfort_offline` files, via `LVX_DATA_ROOT`.
  - **Outputs are committed** to `results/`, and the page names the dataset, sequence and commit.
- **Each chapter is three files:** `course/chapters/<ID>-<slug>/run.py`, `docs/learn/<ID>-<slug>.md`,
  and `tests/course/test_<ID>.py`.
  - Reusable code lives in `course/lvio_course/`, never in `run.py`.
  - Later chapters import earlier modules and **never reimplement** them. Extend a module instead,
    keeping its earlier tests green.
- **No GTSAM, Open3D, ROS or SAD code inside `lvio_course`**, only NumPy/SciPy/Matplotlib. The reader
  must have seen every piece. The C++ labs and "In the real systems" cover the libraries.

**Every chapter page has these sections, in order:**
What you will build · Intuition · The math · Build it · See it · Break it · Run it in C++ (only if the
chapter has SAD labs) · On real data (required for bridge chapters, optional otherwise) · In the real
systems · Experiment hooks · Try it · Next.

**No hand-copied code, output or numbers on a page** (`tools/sync_course.py` fills them, CI checks)
- **Code:** `<!-- snippet:begin run.py#name -->` … `<!-- snippet:end -->`, from `# [snippet:name]`
  regions in `run.py`.
- **Output:** `<!-- output:begin results/run.txt -->` … `<!-- output:end -->`.
- **Prose numbers:** `<!-- m:key/path|fmt -->value<!-- /m -->`, from `results/metrics.json`.
- **Book reference and lab table:** `<!-- course:begin book -->` and `<!-- course:begin labs -->`,
  generated from the curriculum and the recorded lab manifests.
- **After changing a chapter:** run `run.py`, then `python tools/sync_course.py`, and commit the page,
  results and figures together.

**The SAD book and code**
- **Code is MIT; the book is not.** Never copy the book's text, figures or derivations. Link the
  chapter (the English PDF) and build the idea independently, in your own words and code.
- **SAD code is pinned in `systems/systems.yaml` and never vendored.** Point to it with file and
  function names (e.g. `src/ch3/imu_integration.h`).
- **C++ labs are defined in `curriculum.yaml` `labs:` and run only via `lvx lab run <id>`.**
  - The runner uses a scratch sandbox, because SAD apps write into `./data/`. Never run an app in the
    SAD tree itself.
  - It records `manifest.json` and `log_tail.txt` (host paths scrubbed) under the chapter's `results/labs/`.
  - A lab becomes `status: verified` only once a run has been recorded.
  - Numbers from a lab may be quoted only from its recorded files (law 1).
- **Datasets come from `configs/datasets.yaml`:** official links, size and the local path under
  `LVX_DATA_ROOT`. `lvx data check` reports what is present. Never hard-code a dataset path anywhere else.

**Data and honesty**
- **Build it is synthetic-first:** it runs from a fresh clone, with no dataset, in under ~30 s, with fixed seeds.
- **Every claim on the page is asserted** in `tests/course/test_<ID>.py`. If the test can't assert it,
  the page can't claim it.
- **Python speed is never presented as system speed.** Python shows scaling; absolute ms come from
  the C++ labs and the experiments.

**Teaching quality** (docs/process/WRITING_GUIDE.md §7)
- **Intuition before symbols.** Every equation is followed by its symbols in words, with units.
- **See it** has at least one generated figure. **Break it** shows a failure with a number.
  **Try it** has at least two predict-then-run exercises, answers in `<details>`.
- **Experiment hooks** link the ablations that test the idea on GrandTour. Experiment reports link
  back to the chapter in their Discussion.
- **Match the reference chapter**, [B01](docs/learn/B01-imu-propagation.md), in depth and tone.

**Commands:** `/course-chapter <ID>` drafts or updates one chapter. `lvx lab list|run`, `lvx data check`.

## 12. Machine configuration and privacy (nothing device-specific is ever pushed)

**One machine file**
- **`lvx.local.yaml` is the only place for:** paths, ssh aliases, local container tags and private words.
  - It is git-ignored. Create it with `lvx init`; the template is `configs/local.example.yaml`.
  - Environment variables (`LVX_DATA_ROOT`, `LVX_RUN_ROOT`, `LVX_SAD_ROOT`, `LVX_CONFIG`) override it,
    for CI and one-offs.
- **Tracked files use logical names only:**
  - datasets: `sad-ulhk`, `grandtour` (`configs/datasets.yaml`);
  - systems: `sad`, `se3-lvio`, `lightning-lm` (`systems/systems.yaml`, with neutral image tags `lvx/<system>:<tag>`);
  - host profiles: `reference` (`configs/hosts/`, hardware only).

**Code reaches data by name**
- **Datasets:** `from lvx.data import dataset; dataset("sad-ulhk") / "test2.bag"`.
- **Missing data:** `dataset()` raises with the official link and the expected location.
- **Status:** `lvx data check` and `lvx course status` show what this machine can run.
- **Never write** `Path("/…")`, `~/…`, a hostname or a user name in tracked code, configs, docs, reports or commit messages.

**What gets tracked from a run**
- **Manifests:** the command line (which holds local paths) is dropped before a manifest is copied into
  the repo. Images are recorded by content digest, not by local tag.
- **Logs:** tracked log tails go through `course.scrub()`.

**Enforcement**
- `tools/check_tree.py` (CI and the pre-commit hook) rejects machine-specific absolute paths, and any
  word from `private_tokens` in your `lvx.local.yaml`.
- Run `bash scripts/install_hooks.sh` once per clone. It installs the pre-commit hook plus a
  commit-msg hook that checks commit messages too.
- **If you find a leak:** fix it before committing. If it was already committed and not pushed, amend
  or rebase it out. If it was pushed, tell the user; never rewrite pushed history yourself.
