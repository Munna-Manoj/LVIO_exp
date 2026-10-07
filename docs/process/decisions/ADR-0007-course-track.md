# ADR-0007 — The course track

- **Status:** Accepted (2026-10-07). Code layout and page sync superseded by [ADR-0010](ADR-0010-self-contained-chapters.md).

## Context
The repository is also a learning resource for LiDAR-visual-inertial SLAM. Readers learn best by
building one block at a time, and then assembling the blocks. Tutorials usually rot the same way
reports do: copied code drifts from the real code, and numbers in prose stop matching.

## Decision
- **Top level:** a new `course/` directory.
  - `lvio_course/` holds the NumPy building blocks, which grow chapter by chapter.
  - `chapters/<ID>-<slug>/` holds one `run.py` per chapter, plus its generated `results/`.
- **Tracks:** Foundations (F, standalone blocks), then Integration (I, assembled only from earlier
  modules). The curriculum and dependencies live in `docs/learn/README.md`.
- **Pages render on GitHub.** Code, output and prose numbers are filled from the chapter by
  `tools/sync_course.py`, which CI runs with `--check`. This replaces DS-MSP's MkDocs-only include
  macro, which GitHub cannot render.
- **Claims are tested:** every claim on a page has an assertion in `tests/course/test_<ID>.py`.
- **Synthetic data by default;** real-data steps are optional and committed with their provenance.
- **Speed:** Python timings teach scaling only. System speed comes from C++ experiments.

## Consequences
- A chapter costs a program, a page and a test, so chapters stay small and focused.
- The study and the course link each other: chapters have "Experiment hooks", and reports cite chapters.

## Alternatives considered
- **Jupyter notebooks:** hidden state, poor diffs, outputs that drift. They might later be generated
  from `run.py` as a convenience, but are never the source.
- **A C++ course:** closer to the real systems, but much slower to read and to change. The real
  systems themselves are the C++ reference.
