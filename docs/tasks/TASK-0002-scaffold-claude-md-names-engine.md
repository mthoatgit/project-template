# TASK-0002 — State the execution engine in the scaffolded project's CLAUDE.md

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0002** — a scaffolded project states how its tasks are executed and where the engine lives.

## Goal

A session landing in a freshly scaffolded project can learn from `CLAUDE.md` alone that an execution engine exists, how to invoke it, and that its code is installed rather than carried.

**Testability:** structural — a Stage 5 spec asserts the section's content against the template.

## Steps

- Rewrite the `## Implementation` section of `skeleton/CLAUDE.md`. It already names the loop, so this replaces its contents rather than adding a section.
- Give the invocation as the console script — `orchestrator --tasks docs/tasks/ --test-cmd "<test-cmd>" --project-dir .` — rather than `python -m orchestrator`. Both resolve from the installed package, but the console script is the form `consuming-the-orchestrator.md` documents, and it reads less like something the project ships.
- State plainly that the orchestrator is installed and is not part of the repository, and name `~/dev/orchestrator` as its source.
- Keep the existing MUST that Claude uses the orchestrator during implementation and does not implement tasks manually.
- Leave the `<test-cmd>` placeholder intact — `/init-project` fills it, and this task must not change that contract.

## Acceptance Criteria

- `skeleton/CLAUDE.md`'s `## Implementation` section MUST give the console-script invocation.
- It MUST state that the orchestrator is installed rather than contained in the project, and MUST name where its source lives.
- A reader of only that file MUST be able to name both the command that implements tasks and the location of the code implementing it.
- The `<test-cmd>` placeholder MUST survive unchanged, so `/init-project`'s fill step keeps working.
