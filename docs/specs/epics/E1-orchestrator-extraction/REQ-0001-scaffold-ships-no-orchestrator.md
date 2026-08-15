# REQ-0001 — The scaffold ships no orchestrator

**Epic:** E1-orchestrator-extraction
**Status:** active
**Source:** [[035-orchestrator-own-repo-package]]
**Architecture-impact:** none (no ADR)

`skeleton/` MUST NOT contain the orchestrator's source, its test suite, or any configuration that exists only in order to run it. A project created by `/new-project` MUST therefore contain no copy of the loop in any form.

No further mechanism is required for this to hold. `/new-project` copies `skeleton/.` wholesale, so the absence of the directory *is* the mechanism — nothing needs to learn to skip it. Downstream projects obtain the loop from the single shared installation instead, which this project does not arrange per project and does not version.

## Acceptance

A project created by `/new-project` contains no orchestrator module, package, or test file, and the loop runs against that project successfully without any file in the project supplying it.

## Rationale

This is the requirement the source item was filed for. A scaffold ships by copying, and a copy is frozen at the moment it was taken; the loop is the one thing in the scaffold that must never be frozen, because a fix to it has to reach projects that already exist. The drift was not hypothetical — at the time of the item's Stage 1, the vendored copy in `orchestrator-dashboard` carried twelve modules where the other copies carried fourteen, and `project-template`'s own copy had fallen two files behind the real source within a single day.

## Related

- [[REQ-0002]] — removing the copy removes the only visible sign that a loop exists; that requirement supplies the replacement.
- [[REQ-0005]] — the same removal, applied to projects that were scaffolded before this changed.
