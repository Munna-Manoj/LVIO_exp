# ADR-0009 — Machine configuration and privacy

- **Status:** Accepted (2026-10-07). Replaces the `LVX_DATA_ROOT`/`LVX_RUN_ROOT`-only approach of ADR-0006.

## Context
- The repository is public. Early drafts leaked a host name into every spec and report, and a
  user-specific container tag into a lab record.
- Readers also need a clean way to link datasets they downloaded, wherever they put them, to the
  chapters that use them.

## Decision
- **One git-ignored file per machine,** `lvx.local.yaml`, holds paths (`data_root`, `run_root`,
  per-dataset and per-system overrides), ssh aliases (`hosts`), local image tags and `private_tokens`.
  - It is created by `lvx init`; the template is `configs/local.example.yaml`.
  - Environment variables override it for CI.
- **Tracked files use logical names only:**
  - datasets, from `configs/datasets.yaml`, with a default `dir` and the `files` lvx checks;
  - systems, with neutral image tags `lvx/<system>:<tag>`;
  - host *profiles*, which describe hardware only (`reference`).
- **Data access by name:** code reaches data only via `lvx.data.dataset(name)`.
  `lvx data check` and `lvx course status` show what is ready.
- **Sanitised records:** tracked run and lab records drop command lines, record image digests instead
  of tags, and scrub logs.
- **Enforcement:** `tools/check_tree.py` (CI + pre-commit) and a commit-msg hook reject
  machine-specific paths and every private token.

## Consequences
- A new user runs `lvx init` once, downloads data, and `lvx data check` links it to the chapters.
- Private words are checked only where the local file exists (each contributor's machine); CI still
  catches absolute paths.
