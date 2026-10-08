## What and why

<!-- One paragraph. Link the ROADMAP item (M*) or experiment (EXP-*). -->

## Definition of Done (docs/process/DEFINITION_OF_DONE.md)

- [ ] Linked to `M*` / `EXP-*`; ROADMAP.md updated in this PR
- [ ] `ruff`, `pytest`, `check_tree`, `check_experiments`, `check_reports`, `check_chapters`, `check_lie`, `check_links`, `check_math`, `sync_course --check` green
- [ ] Docs updated with the behaviour; `mkdocs build --strict` passes (if docs changed)
- [ ] No personal paths, data, or upstream lightning-lm source
- [ ] Experiment state changes made only by `lvx` (no hand-edited status or `lvx:` blocks)

### If this adds or changes a course chapter
- [ ] Read-aloud test passed; the folder is self-contained (law 0); the output pasted in the README matches `results/output.txt`

### If this freezes an experiment
- [ ] No TODO in frozen fields; one change per variant; decision rule uses the noise floor

### If this concludes an experiment
- [ ] summary.json `complete: true`; figures generated; verdict follows the frozen rule (quoted)
- [ ] TL;DR, discussion, threats to validity, failures written
