# E1 — Orchestrator extraction

**Status:** draft
**Branch:** `epic/1-orchestrator-extraction`
**PR title:** `Epic 1: Orchestrator extraction`
**Source:** [[035-orchestrator-own-repo-package]]

## Goal

After this Epic merges, a reviewer can run `/new-project`, open the result, and find no orchestrator code anywhere in it — while its `CLAUDE.md` states plainly how tasks get implemented and that the engine is installed rather than carried. The reviewer can then check `project-template` itself and find no loop source, no test suite, and no build configuration left behind, and can walk every project under `~/dev` without finding a vendored copy in any of them.

Three of the six requirements deliver changes into repositories this Epic's pull request cannot contain — `dotfiles-claude` for the command text and the availability check, and five downstream project repositories for the de-vendoring. Those are carried as procedural work items and verified by procedural test specs rather than by the diff of this Epic's PR. This is a deliberate structure, decided in the source item's Stage 2: the extraction is not finished while five projects still hold a frozen copy, and splitting the requirement out of the Epic would have moved the boundary problem rather than solved it.

## Functional Requirements

- [**REQ-0001**](REQ-0001-scaffold-ships-no-orchestrator.md) — The scaffold ships no orchestrator. — Architecture-impact: none (no ADR)
- [**REQ-0002**](REQ-0002-scaffolded-project-states-execution.md) — A scaffolded project states how its tasks are executed. — Architecture-impact: none (no ADR)
- [**REQ-0003**](REQ-0003-report-missing-installation.md) — Scaffolding reports a missing shared installation. — Architecture-impact: ADR-0002 (console-script resolution, scaffold-time only, per-venv blind spot accepted)
- [**REQ-0004**](REQ-0004-no-orchestrator-artefacts-retained.md) — `project-template` retains no orchestrator artefacts. — Architecture-impact: none (no ADR)
- [**REQ-0005**](REQ-0005-devendor-existing-projects.md) — Projects that already vendored the loop are de-vendored. — Architecture-impact: none (no ADR)
- [**REQ-0006**](REQ-0006-commands-drop-bundled-assumptions.md) — The workflow commands do not instruct on a bundled orchestrator. — Architecture-impact: none (no ADR)
