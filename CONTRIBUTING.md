# Contributing

Thanks for helping. This repository is a controlled study, so contributions follow a fixed path. The
rules are in [CLAUDE.md](CLAUDE.md) (for people and AI assistants alike) and the
[experiment protocol](docs/process/EXPERIMENT_PROTOCOL.md).

## TL;DR

1. **Branch:** `exp/EXP-NNN-<slug>`, `infra/<topic>` or `docs/<topic>`. No direct commits to `main`.
2. **New experiment:** `lvx exp new <slug> --phase Pn`, fill the spec, open a PR for approval.
   Run nothing before `lvx exp freeze`.
3. **System code changes** go to the SE(3)-LVIO fork (`systems/se3-lvio`, branch `lvio-exp`), behind
   one flag whose default keeps the baseline.
4. **Run the gates:**
   ```bash
   ruff check lvx tools tests
   pytest -q
   python tools/check_tree.py
   python tools/check_experiments.py
   python tools/check_reports.py
   mkdocs build --strict
   ```
5. **Commit:** Conventional Commits with the ID in the scope (`feat(EXP-003): …`).
6. **Open the PR.** Its template is the [Definition of Done](docs/process/DEFINITION_OF_DONE.md).
