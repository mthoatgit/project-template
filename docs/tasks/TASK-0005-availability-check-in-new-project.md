# TASK-0005 — Add the availability check to `/new-project`

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0003** — scaffolding reports a missing shared installation.

## Related ADRs

- **ADR-0002** — fixes what the check inspects (the console script, not a clone directory), when it runs (scaffold time only), that it MUST NOT fail the scaffold, and that no per-project installation state may be written.

## Goal

A user scaffolding a project on a machine without the orchestrator learns so at the moment it matters, instead of at the first invocation with an error that points nowhere near its cause.

**Testability:** procedural — verified by running `/new-project` in both states, since the change lands in `dotfiles-claude` and there is nothing in this repository to assert against.

## Steps

- Edit `~/.claude/commands/new-project.md` — a file in the separate `dotfiles-claude` repository, which this Epic's pull request cannot contain. Commit it there.
- Add a step that resolves the `orchestrator` console script and reports failure. Place it late enough that it never blocks the scaffold, and early enough that its output is not buried under the rest of the run.
- Write the failure message to name both causes — no clone, or a clone that was never installed — with the two commands from `consuming-the-orchestrator.md`. One check, complete message; ADR-0002 rejected probing twice to discriminate.
- State in the message that the project was created successfully regardless, so the report is not read as a failure.
- Do not write anything into the scaffolded project. ADR-0002 forbids per-project installation state, and a note recorded there would be exactly that.

## Acceptance Criteria

- `/new-project` MUST determine availability by resolving the `orchestrator` console script, and MUST NOT infer it from a directory's presence.
- A failed resolution MUST produce a report naming both causes and both remedies, and MUST NOT abort the scaffold — the project MUST still be complete.
- A successful resolution MUST produce no report.
- The scaffolded project MUST contain no file recording the check, its result, or the installation.

## Dependencies

None within this Epic. The check describes a machine state that already exists and does not depend on any deletion here.
