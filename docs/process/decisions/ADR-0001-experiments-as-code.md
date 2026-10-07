# ADR-0001 — Experiments are code

- **Status:** Accepted (2026-10-07)

## Context
Ablation studies rot in one of three ways:
- numbers lose their provenance;
- hypotheses get rewritten after the data comes in;
- one-off scripts multiply until nobody can reproduce a figure.

This repository is also a public portfolio, so every claim must survive a sceptical reader.

## Decision
- Every experiment is a YAML spec. Its pre-registered fields are hashed into `spec.lock` before the first run.
- Only `lvx` executes runs, writes results and changes the status. Each run has a manifest (commits, config hash, image digest, host).
- Reports have a fixed shape. Their data blocks are generated, and CI fails on hand edits (`check_reports.py`).
- The registry and the README index are generated from the specs.

## Consequences
- Adding an experiment costs a spec and an approval before any compute. That is intended.
- A rerun is a new repeat, never an overwrite. Bad news is kept.

## Alternatives considered
- MLflow / W&B: built for ML training metrics, and add a server; they don't enforce pre-registration.
- Notebooks: they mix code and results and hide state.
