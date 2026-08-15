# REQ-0007 — The one project that vendored the loop is de-vendored

**Epic:** E1-orchestrator-extraction
**Status:** active
**Supersedes:** REQ-0005
**Source:** [[035-orchestrator-own-repo-package]]
**Architecture-impact:** none (no ADR)

`orchestrator-dashboard` MUST have its vendored copy of the orchestrator removed, and MUST state where the loop lives instead — to the same standard `REQ-0002` sets for newly scaffolded projects.

It MUST be treated as the exception it is. It predates the current layout, carrying an older `orchestrator/tests/` directory and its own `pytest.ini`, and it consumes the loop's *output* — it reads `docs/tasks/index.md` from driven projects — as well as having vendored its code. Removing the vendored copy MUST NOT disturb that second relationship.

## Acceptance

No project under `~/dev` holds an orchestrator source directory, and `orchestrator-dashboard` names the external engine in its own `CLAUDE.md`. It still reads and renders the work-item indexes of the projects it reports on.

## Rationale

This requirement is `REQ-0005` narrowed. That version named five vendored projects. Four of them — `dice-roller`, `kitchen-inventory`, `palette-picker`, and `wordfreq` — turned out to be disposable test beds rather than projects anyone depended on, and were deleted outright on 2026-08-15 rather than de-vendored. What that leaves is not a smaller version of the same job: the four were mechanically uniform and the one that remains is the awkward case, so the requirement is now entirely about the exception.

The reason for de-vendoring at all is unchanged from `REQ-0005`. A vendored copy keeps working, because it is self-contained; what it does not do is receive fixes, which is the whole reason the extraction happened. The dashboard's copy already shows the drift — twelve modules where the current source carries fourteen.

## Related

- [[REQ-0005]] — superseded by this one; its text is the historical record of the five-project scope.
- [[REQ-0001]] — the forward-path half of the same removal.
- [[REQ-0002]] — the standard this requirement applies retroactively.
