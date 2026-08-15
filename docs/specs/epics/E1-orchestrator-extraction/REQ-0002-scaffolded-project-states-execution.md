# REQ-0002 — A scaffolded project states how its tasks are executed

**Epic:** E1-orchestrator-extraction
**Status:** active
**Source:** [[035-orchestrator-own-repo-package]]
**Architecture-impact:** none (no ADR)

Every project created by `/new-project` MUST state, in its own `CLAUDE.md`, the command that runs the implementation loop, the fact that the loop is installed rather than contained in the repository, and where its source lives. The statement MUST be present from the moment the project is scaffolded — not added later by a stage the project may never reach.

## Acceptance

A session that opens a freshly scaffolded project and reads only its `CLAUDE.md` can name the command that implements tasks and say where the code implementing it lives, without inspecting any other file in the project and without prior knowledge of this machine's layout.

## Rationale

De-vendoring removes evidence, not capability. Technically a project needs nothing: the editable install puts the `orchestrator` console script on `PATH` and makes `python -m orchestrator` resolve from any working directory, so the loop runs against a project that contains no trace of it. Today one trips over an `orchestrator/` directory and learns the loop exists by accident. Afterwards nothing in the project would mention it, and a session landing in a downstream project would have no way to discover that an execution engine exists at all — the project would be runnable and the loop unfindable.

The replacement is already half-built: `skeleton/CLAUDE.md` carries an `## Implementation` section that names the loop but gives an invocation form only, with no indication that the code is external. What this requirement adds is the missing half — that the engine is installed, and where it comes from.

## Related

- [[REQ-0001]] — removing the vendored copy is what creates the visibility gap this requirement closes.
- [[REQ-0005]] — extends the same statement to projects that were scaffolded before this existed.
