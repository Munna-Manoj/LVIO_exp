# Architecture decision records

| ADR | Decision | Status |
|---|---|---|
| [ADR-0001](ADR-0001-experiments-as-code.md) | Experiments are code: pre-registered specs, generated results and reports | Accepted |
| [ADR-0002](ADR-0002-evaluation-protocol.md) | One evaluation protocol for every system (COMFORT ATE, prism frame) | Accepted |
| [ADR-0003](ADR-0003-system-inclusion-and-licences.md) | How the two systems are included, given GPL-2.0 and no-licence upstreams | Accepted |
| [ADR-0004](ADR-0004-noise-floor-decision-rule.md) | Effects must exceed 2σ run-to-run noise | Accepted |
| [ADR-0005](ADR-0005-mission-split.md) | Tune on dev, report on test | Proposed (split fixed in M0.5) |
| [ADR-0006](ADR-0006-data-and-artifacts.md) | Data and large artefacts stay out of git; what is tracked | Accepted |
| [ADR-0007](ADR-0007-course-track.md) | The course track: building blocks, synced pages, tested claims | Partly superseded by ADR-0010 |
| [ADR-0008](ADR-0008-sad-book-integration.md) | SAD book as the course backbone, real systems as the capstone, C++ labs | Accepted |
| [ADR-0009](ADR-0009-machine-config-and-privacy.md) | One git-ignored machine file; tracked files use logical names only; leak checks | Accepted |
| [ADR-0010](ADR-0010-self-contained-chapters.md) | Self-contained chapters: readability over reuse (law 0) | Accepted |

Template: Context → Decision → Consequences → Alternatives considered. A new ADR is required for a new
top-level directory, a new dependency, a change to the evaluation protocol, or a change to the split.
