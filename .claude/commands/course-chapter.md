---
description: Draft or update one course chapter following CLAUDE.md §11
argument-hint: <chapter ID, e.g. C02> [focus]
---
Work on course chapter $ARGUMENTS.

1. **Read the plan:**
   - `course/curriculum.yaml`: the chapter row (part, SAD chapter + apps, labs, depends_on, experiments).
   - The SAD book chapter (English PDF) and its `src/ch<N>` code, to know what the C++ lab shows. Never copy the book.
   - CLAUDE.md §11.
   - `docs/learn/B01-imu-propagation.md` + `course/chapters/B01-imu-propagation/run.py`: the reference chapter.
   - Confirm the prerequisites exist; if not, stop and say which one is missing.
2. **Propose an outline to the user first:**
   - the intuition;
   - the equations;
   - the 3–5 build steps;
   - the figures;
   - the "break it" failure;
   - the claims the test will assert.

   Wait for approval.
3. **Implement:**
   - reusable code in `course/lvio_course/` (extend, never duplicate);
   - `course/chapters/<ID>-<slug>/run.py` with `# [snippet:…]` regions, writing `results/run.txt` (stdout) and `results/metrics.json`;
   - figures with `lvx.plotstyle` into `docs/assets/learn/<ID>/`.
4. **Write the page** `docs/learn/<ID>-<slug>.md` with the 10 sections. Use snippet/output/metric
   markers, never typed-in code or numbers.
5. **Write the test:** `tests/course/test_<ID>.py` asserts every claim the page makes.
6. **Sync and check:**
   - `python course/chapters/<ID>-<slug>/run.py > course/chapters/<ID>-<slug>/results/run.txt`
   - `python tools/sync_course.py`
   - then every check in CLAUDE.md §8.
7. **If it is a 🔗 bridge chapter (I..):** write the required "On real data" step in run.py (or a
   `real.py` region). It reads the listed `datasets` via `LVX_DATA_ROOT` (`rosbags` for SAD bags,
   `comfort_offline` for GrandTour). Commit its outputs, and name dataset + sequence + commit on the page.
   **If the chapter has labs:** run each with `lvx lab run <id>` on the host, `lvx sync`-pull the records,
   set the lab `status: verified`, and write the "Run it in C++" section around the generated lab table.
8. **Update the bookkeeping:** the curriculum status, the ROADMAP C-milestone row, and the mkdocs nav.
   Look at every figure before calling it done.
