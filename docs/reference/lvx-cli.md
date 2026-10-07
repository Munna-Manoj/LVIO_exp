# lvx CLI

| Command | Changes | Allowed when |
|---|---|---|
| `lvx exp new <slug> --phase Pn [--supersedes EXP]` | creates spec + report skeleton | always |
| `lvx exp freeze EXP --approved-by <handle>` | writes `spec.lock`, status → approved | status planned, no TODO |
| `lvx run EXP [--variant v] [--mission m] [--dry-run]` | run dirs + manifests, status → running | approved / running / analysed |
| `lvx eval EXP` | `runs.csv`, `summary.json`, manifests + repeat-1 trajectories in git, status → analysed | runs exist |
| `lvx figures EXP` | `docs/assets/experiments/EXP/*.png` | summary exists |
| `lvx report [EXP] [--index]` | the report's `lvx:` blocks; registry + README index | always |
| `lvx exp conclude EXP --verdict adopt\|reject\|inconclusive` | status → concluded | analysed, report written |
| `lvx exp abandon EXP --reason "…"` | status → abandoned | not concluded |
| `lvx sync EXP\|chapter --host reference` | pulls tracked results from the machine that plays the profile | its entry in lvx.local.yaml |
| `lvx init --data-root D --run-root R [--dataset N=DIR] [--system S.root=DIR] [--private-token W]` | writes the git-ignored `lvx.local.yaml` | always |
| `lvx config show` / `lvx config get dataset sad-ulhk` | prints the resolved machine configuration | – |
| `lvx data check` | every dataset: where lvx looks, ready or missing, which chapters use it | – |
| `lvx course status` | which chapters' real-data steps and C++ labs can run on this machine | – |
| `lvx lab list` / `lvx lab run <lab>` | SAD C++ labs in a sandbox, recorded manifest | the SAD build + the lab's dataset |
