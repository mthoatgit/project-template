# REQ-0005 — Projects that already vendored the loop are de-vendored

**Epic:** E1-orchestrator-extraction
**Status:** superseded
**Superseded by:** REQ-0007
**Source:** [[035-orchestrator-own-repo-package]]
**Architecture-impact:** none (no ADR)

Every project on the machine that holds a vendored copy of the orchestrator MUST have that copy removed, and MUST state where the loop lives instead — to the same standard `REQ-0002` sets for newly scaffolded projects. The projects are `dice-roller`, `kitchen-inventory`, `orchestrator-dashboard`, `palette-picker`, and `wordfreq`.

Each project's own `CLAUDE.md` MUST be corrected in the same pass: all five carry an `## Implementation` section giving an invocation form with no indication that the engine is external.

`orchestrator-dashboard` MUST be treated as the exception it is. It predates the current layout, carrying an older `orchestrator/tests/` directory and its own `pytest.ini`, and it consumes the loop's *output* — it reads `docs/tasks/index.md` from driven projects — as well as having vendored its code. Removing the vendored copy MUST NOT disturb that second relationship.

## Acceptance

No project under `~/dev` holds an orchestrator source directory, and each of the five formerly-vendored projects names the external engine in its own `CLAUDE.md`. `orchestrator-dashboard` still reads the work-item indexes of the projects it reports on.

## Rationale

The source item frames the pain as projects that already scaffolded being stuck with a frozen snapshot, and leaving those five untouched would leave the item's own stated problem standing in every project that has it. The user's framing in Stage 1 reached for this directly — *"nicht mehr im skeleton ... und auch nicht in den downstream projekten"*.

Nothing here is urgent in the failure sense: a vendored copy keeps working, because it is self-contained. What it does not do is receive fixes, which is the whole reason the extraction happened.

## Related

- [[REQ-0001]] — the forward-path half of the same removal.
- [[REQ-0002]] — the standard this requirement applies retroactively.
