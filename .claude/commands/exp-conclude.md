---
description: Write the analysis sections of a report and conclude the experiment
argument-hint: <EXP-NNN>
---
Conclude $ARGUMENTS following CLAUDE.md §4 and docs/process/WRITING_GUIDE.md:
1. Read the frozen decision rule in spec.yaml and the generated Results block. Derive the verdict
   **mechanically** from the rule. Quote the rule.
2. Write, outside the `lvx:` blocks:
   - **TL;DR:** one sentence with the number.
   - **Observations:** ≤ 5 bullets, each pointing to a cell or figure.
   - **Discussion:** why it happened; link docs/explain.
   - **Verdict.**
   - **Threats to validity.**
   - **Failures.**
3. Every number you write must appear in summary.json or runs.csv. Cite the experiment ID.
4. Show the draft to the user. After approval:
   - `lvx exp conclude <EXP> --verdict …`
   - `lvx report --index`
   - update ROADMAP.md
   - run the checkers
   - commit `docs(<EXP>): verdict`
