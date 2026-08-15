# E1 — Orchestrator extraction

**Status:** merged
**Branch:** `epic/1-orchestrator-extraction` — fast-forwarded into `main` on 2026-08-15 without a pull request, by the user's decision. Each task commit is preserved on `main`; the `/ship-epic` self-review and Reflect step were not run.
**PR title:** `Epic 1: Orchestrator extraction` (never opened)
**Source:** [[035-orchestrator-own-repo-package]]

## Goal

After this Epic merges, a reviewer can run `/new-project`, open the result, and find no orchestrator code anywhere in it — while its `CLAUDE.md` states plainly how tasks get implemented and that the engine is installed rather than carried. The reviewer can then check `project-template` itself and find no loop source, no test suite, and no build configuration left behind, and can walk every project under `~/dev` without finding a vendored copy in any of them.

Three of the requirements deliver changes into repositories this Epic's pull request cannot contain — `dotfiles-claude` for the command text and the availability check, and `orchestrator-dashboard` for the de-vendoring. Those are carried as procedural work items and verified by procedural test specs rather than by the diff of this Epic's PR. This is a deliberate structure, decided in the source item's Stage 2: the extraction is not finished while a project still holds a frozen copy, and splitting the requirement out of the Epic would have moved the boundary problem rather than solved it.

## Functional Requirements

- [**REQ-0001**](REQ-0001-scaffold-ships-no-orchestrator.md) — The scaffold ships no orchestrator. — Architecture-impact: none (no ADR)
- [**REQ-0002**](REQ-0002-scaffolded-project-states-execution.md) — A scaffolded project states how its tasks are executed. — Architecture-impact: none (no ADR)
- [**REQ-0003**](REQ-0003-report-missing-installation.md) — Scaffolding reports a missing shared installation. — Architecture-impact: ADR-0002 (console-script resolution, scaffold-time only, per-venv blind spot accepted)
- [**REQ-0004**](REQ-0004-no-orchestrator-artefacts-retained.md) — `project-template` retains no orchestrator artefacts. — Architecture-impact: none (no ADR)
- [**REQ-0005**](REQ-0005-devendor-existing-projects.md) — ~~Projects that already vendored the loop are de-vendored~~ (superseded by REQ-0007)
- [**REQ-0006**](REQ-0006-commands-drop-bundled-assumptions.md) — The workflow commands do not instruct on a bundled orchestrator. — Architecture-impact: none (no ADR)
- [**REQ-0007**](REQ-0007-devendor-the-dashboard.md) — The one project that vendored the loop is de-vendored. — Architecture-impact: none (no ADR)

## Tasks

- [TASK-0001 — Remove the vendored orchestrator from the scaffold](../../../tasks/TASK-0001-remove-orchestrator-from-skeleton.md)
- [TASK-0002 — State the execution engine in the scaffolded project's CLAUDE.md](../../../tasks/TASK-0002-scaffold-claude-md-names-engine.md)
- [TASK-0003 — Remove project-template's own orchestrator artefacts](../../../tasks/TASK-0003-remove-own-orchestrator-artefacts.md)
- [TASK-0004 — Rewrite project-template's self-description](../../../tasks/TASK-0004-rewrite-self-description.md)
- [TASK-0005 — Add the availability check to `/new-project`](../../../tasks/TASK-0005-availability-check-in-new-project.md)
- [TASK-0006 — Drop the bundled-orchestrator instructions from the scaffolding commands](../../../tasks/TASK-0006-drop-bundled-orchestrator-instructions.md)
- [TASK-0008 — De-vendor `orchestrator-dashboard`](../../../tasks/TASK-0008-devendor-orchestrator-dashboard.md)

Only TASK-0001 through TASK-0004 land in this repository and therefore in this Epic's pull request. TASK-0005 and TASK-0006 commit into `dotfiles-claude`; TASK-0008 commits into `orchestrator-dashboard`.

`TASK-0007` — de-vendor the four uniform downstream projects — was retired unimplemented on 2026-08-15 when those four projects were deleted rather than de-vendored, along with the `REQ-0005` it served. Its ID is burned and is not reused; the next task filed in this project is `TASK-0009`.

## Implementation note

This Epic is implemented manually rather than by the orchestrator, and it is the only Epic for which that is true by design.

TASK-0003 deletes `pytest.ini` and `orchestrator-tests/` — this repository's entire test infrastructure — and [ADR 0003](../../../adr/0003-medium-and-dependencies.md) then commits the project to having none, with correctness established by inspection. The orchestrator refuses a task whose `--test-cmd` target does not exist and hard-aborts a task with no primary-anchored TEST file, so the Epic that removes the test infrastructure cannot be driven by a loop requiring it. Stage 5 therefore produces structural specs for the in-repository tasks and procedural specs for the cross-repository ones, all verified by inspection.

The rest of the ceremony is unchanged: the Epic has its branch, its pull request, and its end-of-Epic self-review.

## Epic-Level Acceptance Criteria

- A project created by `/new-project` MUST contain no orchestrator source, and the loop MUST run against it successfully from the shared installation.
- That project's `CLAUDE.md` MUST state the invocation, MUST state that the engine is installed rather than carried, and MUST name where its source lives — readable without opening any other file.
- `/new-project` MUST report a missing installation, naming both causes and both remedies, without failing the scaffold.
- This repository MUST contain no orchestrator source, no test suite, no `pytest.ini`, and no document specifying the loop; its `CLAUDE.md` and `README.md` MUST make no claim to own, test, or specify it.
- No project under `~/dev` MUST hold a vendored orchestrator directory, and `orchestrator-dashboard` MUST name the external engine.
- `orchestrator-dashboard` MUST still read and render the work-item indexes of the projects it reports on.
- Neither `/init-project` nor `/new-project` MUST carry instructions about removing orchestrator files from a scaffolded project, and `/scaffold` MUST be unchanged.
