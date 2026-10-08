---
description: Draft or update one course chapter following CLAUDE.md law 0 and §11
argument-hint: <chapter ID, e.g. C02> [focus]
---
Work on course chapter $ARGUMENTS.

1. **Read the plan:**
   - `course/curriculum.yaml`: the chapter row (part, SAD chapter + apps, labs, depends_on, experiments, `scene`).
   - The SAD book chapter (English PDF) and its `src/ch<N>` code, to know what the C++ lab shows. Never copy the book.
   - CLAUDE.md law 0 and §11.
   - For 3D maths or optimisation: DS-MSP `ds_msp/core/` (`lie.py`, `optimize.py`, `robust.py`,
     `covariance.py`) and `tools/lie_reference.py`. Use its names and copy its bodies; propose a better
     formulation to the user instead of silently deviating (it goes to DS-MSP first).
   - `course/chapters/A01-rotations-and-poses/`, the reference chapter (lessons, template 2): README.md,
     then the .py files, then the `live_*.py` animations.
2. **Propose an outline to the user first:**
   - the synthetic scene and the money plot (from `scene:`; suggest a better-known example if there is one);
   - the lessons (one idea each), and for each the ladder of CLAUDE.md §11: the plain question, the one
     sample worked step by step (and its animation), the two ways fed the same inputs, the knob, the
     misconceptions a learner will have, the check-yourself questions;
   - the numbered equations;
   - the files, one per idea, and which helpers get copied from which earlier chapter;
   - the claims the test will assert.

   Wait for approval.
3. **Implement in the chapter folder only:**
   - `<idea>.py` files plus `main.py`;
   - imports only stdlib, numpy, scipy, matplotlib (rosbags for real data) and the folder's own files;
   - every equation line ends with `# (Eq. n)`;
   - plain functions and arrays, symbol names, explicit loops;
   - `main.py` prints the results, writes `results/output.txt`, `results/metrics.json` and the figures.
4. **Write `README.md` by hand,** with the sections in order and each lesson on the ladder. Put the money plot at the top, tag the
   equations with `\qquad (n)` in ` ```math ` fences (inline maths `` $`…`$ ``), paste `results/output.txt` verbatim in a ```text block, and take every
   result number from that output.
5. **Write the test:** `tests/course/test_<ID>.py` asserts every claim the README makes, from `metrics.json`.
6. **Check:**
   - `cd course/chapters/<ID>-<slug> && python main.py` (≤ ~30 s);
   - look at every figure;
   - do the read-aloud test (DoD), then ask the user to be the first reader: every question they ask
     becomes a step, figure or misconception in the chapter;
   - run every check in CLAUDE.md §8, including `python tools/check_chapters.py` and `python tools/check_lie.py`.
7. **If it is a 🔗 bridge chapter (I..):** write the "On real data" step. It reads the listed `datasets`
   from a directory passed on the command line (`python main.py --data <dir>`), with `rosbags` for SAD
   bags or the `comfort_offline` files for GrandTour. Commit its outputs, and name dataset, sequence and
   commit in the README.
   **If the chapter has labs:** the README shows the plain SAD command. Record each with
   `lvx lab run <id>` on the host, pull the records, and set the lab to `status: verified`.
8. **Update the bookkeeping:** the curriculum status, the ROADMAP C-milestone row, and the mkdocs nav
   (`learn/<ID>-<slug>/index.md`).
