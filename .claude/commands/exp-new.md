---
description: Draft a new pre-registered experiment spec (does not freeze or run it)
argument-hint: <slug> <phase P0-P7|PX> <one-line idea>
---
Draft an experiment for: $ARGUMENTS

Follow CLAUDE.md §2 and docs/process/EXPERIMENT_PROTOCOL.md §3 strictly:
1. Check `experiments/registry.md` and ROADMAP.md for an existing experiment on the same question.
   If one exists, stop and say so.
2. Run `lvx exp new <slug> --phase <phase>`.
3. Fill every field of the new spec.yaml:
   - one question;
   - a hypothesis with a mechanism;
   - a prediction with direction and size;
   - a falsification outcome;
   - variants with exactly ONE change each;
   - missions from configs/missions.yaml;
   - repeats ≥ 3;
   - a decision rule that uses the 2σ noise floor;
   - depends_on.
4. Add the experiment to the ROADMAP.md catalogue table.
5. Run `lvx report <EXP>`, `lvx report --index`, then all checkers.
6. Show the user the filled spec and ask for approval. **Never run `lvx exp freeze` without an explicit "approved".**
