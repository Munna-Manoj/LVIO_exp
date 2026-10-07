# Spec fields

`🔒` marks a pre-registered field, hashed into `spec.lock` by `lvx exp freeze`.

| Field | Type | Meaning |
|---|---|---|
| `id`, `slug` | str | `EXP-NNN`, kebab-case; the folder is `<id>-<slug>` |
| `title` | str | the question, phrased as a title |
| `phase` | P0–P7, PX | see the ROADMAP phases |
| `status` | enum | planned → approved → running → analysed → concluded / abandoned; changed only by lvx |
| `system` | se3-lvio, lightning-lm, both | system under test |
| `depends_on` | [EXP] | must be concluded before this one runs |
| `host` 🔒 | str | `configs/hosts/<name>.yaml` |
| `question` 🔒 | str | one question, answerable by the primary metric |
| `hypothesis` 🔒 | str | the belief and its mechanism |
| `prediction` 🔒 | str | direction and rough size of the outcome |
| `falsified_if` 🔒 | str | the outcome that would refute the hypothesis |
| `baseline` 🔒 | str | `configs/baselines/<name>.yaml` |
| `variants` 🔒 | list | `{id, change, overrides \| modes_add \| modes_remove \| baseline}`, one change each |
| `missions` 🔒 | map | `{set: dev}` or `{list: [...]}` |
| `repeats` 🔒 | int | runs per variant × mission |
| `metrics` 🔒 | map | `primary` + `secondary` from `lvx.spec.METRICS` |
| `stress` 🔒 | str / null | profile in `configs/stress.yaml` |
| `decision_rule` 🔒 | str | how the verdict follows from the numbers |
| `code_change` | str | the flag(s) added in the system fork |
| `learn_links` | [path] | explanation / tutorial pages this experiment teaches |
