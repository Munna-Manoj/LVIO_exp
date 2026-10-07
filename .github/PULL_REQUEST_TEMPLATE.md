## What and why

<!-- One paragraph. Link the ROADMAP item (M*) or experiment (EXP-*). -->

## Definition of Done (docs/process/DEFINITION_OF_DONE.md)

- [ ] Linked to `M*` / `EXP-*`; ROADMAP.md updated in this PR
- [ ] `ruff`, `pytest`, `check_tree`, `check_experiments`, `check_reports` green
- [ ] Docs updated with the behaviour; `mkdocs build --strict` passes (if docs changed)
- [ ] No personal paths, data, or upstream lightning-lm source
- [ ] Experiment state changes made only by `lvx` (no hand-edited status or `lvx:` blocks)

### If this freezes an experiment
- [ ] No TODO in frozen fields; one change per variant; decision rule uses the noise floor

### If this concludes an experiment
- [ ] summary.json `complete: true`; figures generated; verdict follows the frozen rule (quoted)
- [ ] TL;DR, discussion, threats to validity, failures written
