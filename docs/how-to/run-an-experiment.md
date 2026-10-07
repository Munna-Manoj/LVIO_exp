# Run an experiment

From a frozen spec to a concluded report. Runs execute on the compute host, where the data lives.

## 1. Dry run

```bash
lvx run EXP-001 --dry-run         # prints the first run's manifest: command, config hash, commits
```

## 2. Run everything (on the host, in the background)

```bash
# on the machine that plays host profile `reference` (its ssh alias is in your lvx.local.yaml)
nohup lvx run EXP-001 > lvx_EXP-001.log 2>&1 &
```

Runs are append-only: `<run_root>/EXP-001/<variant>/<mission>/r<k>/` (run_root from `lvx.local.yaml`). Re-running the command
continues where it stopped; it never overwrites.

## 3. Evaluate, plot, report

```bash
lvx eval EXP-001                  # runs.csv + summary.json; status -> analysed when complete
lvx figures EXP-001               # effect.png, pareto.png, error_time.png, traj_top.png
lvx report EXP-001                # regenerate the report's data blocks
```

From a laptop, pull the small results back:

```bash
lvx sync EXP-001 --host reference      # ssh alias + checkout path come from lvx.local.yaml
```

## 4. Write the analysis, then conclude

Write the TL;DR, observations, discussion, verdict, threats to validity and failures in
`docs/experiments/EXP-001-*.md`. Then conclude:

```bash
lvx exp conclude EXP-001 --verdict reject     # the verdict must follow the frozen decision rule
lvx report --index                            # registry + README table
```
