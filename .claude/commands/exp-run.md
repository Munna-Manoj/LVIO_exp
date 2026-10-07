---
description: Run, evaluate, plot and report a frozen experiment
argument-hint: <EXP-NNN>
---
Execute $ARGUMENTS following CLAUDE.md §2, §3 and §9:
1. Confirm the spec is `approved`/`running`/`analysed` and `spec.lock` matches (`tools/check_experiments.py`).
   Confirm every `depends_on` is concluded. If not, stop.
2. Confirm the code is committed (lvx refuses dirty code; never pass `--allow-dirty` without the user's say-so).
3. `lvx run <EXP> --dry-run` and show the command + config hash.
4. Start the runs on the host in the background with a log; report progress, don't block.
5. When done:
   - `lvx eval`
   - `lvx figures`
   - `lvx report`
   - `lvx sync` if remote
6. Report the generated results table verbatim, plus the failed runs. **Do not** write the Discussion
   or Verdict yet; ask the user to review the numbers first.
