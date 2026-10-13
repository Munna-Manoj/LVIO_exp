# ADR-0013 — Modifying lightning-lm in a private fork

- **Status:** Accepted (2026-10-13). Replaces the lightning-lm parts of ADR-0003 and of ADR-0012 ("lightning-lm stays reference-only").

## Context
- The owner wants every ablation to cover all three systems: SE(3)-LVIO, lightning-lm and GenZ-LIO (ADR-0012).
- Until now lightning-lm ran unmodified (ADR-0003). Its upstream repository, `gaoxiang12/lightning-lm`, has no licence. As a result, lightning-lm could only take part in ablations where the change is a config key.
- Under copyright law, code without a licence is "all rights reserved". Nobody else is granted the right to copy, modify or redistribute lightning-lm's code. Mentioning the missing licence in our documents does not grant that right.
- Modifying a private copy for research and publishing only results is the use with the lowest risk. A public fork or a copy inside this repository would redistribute the code.

## Decision
- **The owner decided to modify lightning-lm for the ablations.** Its code changes live in a **private** fork, `Munna-Manoj/lightning-lm-lvio`, on branch `lvio-exp`.
  - The fork starts at the upstream commit already pinned (`1325fed`).
  - Each ablation adds one config flag to lightning-lm. The flag's default reproduces upstream behaviour, as in the other two forks.
  - The fork stays private. It is never made public, never added to this repository as a submodule, and never copied into this repository.
- **What this repository publishes about lightning-lm:**
  - our own files only: the headless runner, the bag converter, the Containerfile, and override YAMLs that list only the keys we change;
  - results;
  - a description in words of each change (what the flag does and why). Diffs or excerpts of the fork are never published.
- **Build.** `scripts/build_lightning.sh` clones the private fork at the commit pinned in `systems/systems.yaml`.
  - A host that cannot reach GitHub uses a local mirror of the fork. The mirror's location is set in the git-ignored `lvx.local.yaml` (`systems.lightning-lm.source`).
  - A pin change is its own commit and reruns EXP-000, as before.
- **Disclosure.** The README and LICENSING.md state that lightning-lm has no licence, that we modified it in a private fork for research, and that the modified code is not redistributed.
- **Licence request.** The owner may ask upstream to add a licence. If a licence that permits it is added, a later ADR can make the fork public.

## Consequences
- Ablation specs can now give lightning-lm its own variants. They follow the pattern GenZ-LIO uses (ADR-0012 addendum):
  - a plain `lightning` variant runs lightning-lm's stock config;
  - each lightning-lm variant names `lightning` as its `reference`, so it still differs from its reference in one change (law 4);
  - its noise floor comes from EXP-000, which measured `lightning_stock` and `lightning_indoor`.
- Fork flags are written in the overrides as `lvio_exp.<flag>`. A flag is added to the fork before its experiment is frozen.
- Other people cannot reproduce lightning-lm's ablation runs without access to the private fork. Each report says so under threats to validity.
- `tools/check_tree.py` still rejects any lightning-lm file under `systems/lightning-lm/` that is not one of our own.

## Alternatives considered
- **A public fork, like GenZ-LIO's.** Rejected: GitHub's terms allow forking a public repository, but they do not clearly allow publishing modifications to unlicensed code.
- **Copying the modified code into this repository.** Rejected: it would redistribute unlicensed code in a public repository and site.
- **Keeping lightning-lm reference-only (ADR-0012).** Rejected by the owner: every study should cover all three systems.
