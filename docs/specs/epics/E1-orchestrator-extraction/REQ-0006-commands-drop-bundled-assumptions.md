# REQ-0006 — The workflow commands do not instruct on a bundled orchestrator

**Epic:** E1-orchestrator-extraction
**Status:** active
**Source:** [[035-orchestrator-own-repo-package]]
**Architecture-impact:** none (no ADR)

The `/new-project` and `/init-project` commands MUST NOT carry instructions that presuppose an orchestrator directory inside a project. Two passages qualify: `/init-project`'s step-0 backwards-compat wipe, which removes `orchestrator/tests/` and `pytest.ini` from a freshly cloned target, and `/new-project`'s step-6 aside stating that the skeleton starts clean with *"no orchestrator tests to remove, no pytest.ini to strip"*.

Nothing else in `~/.claude` requires change for this Epic. In particular `/scaffold` MUST be left alone: its `python -m orchestrator` invocation keeps resolving from the installed package regardless of working directory, and the six other files mentioning the orchestrator describe the loop's role rather than its location.

## Acceptance

Neither command's text refers to removing orchestrator files from a scaffolded project, and a `/init-project` run against a fresh scaffold performs no orchestrator-related step.

## Rationale

Neither passage breaks anything — both describe a directory that can no longer exist, and both degrade to no-ops. They are in scope because the alternative is that nothing tracks them: `~/.claude` is the separate `dotfiles-claude` repository and has no backlog of its own, so instructions not claimed by an item here are claimed nowhere. Dead text that describes a vanished layout is how the next reader learns the wrong model.

## Related

- [[REQ-0003]] — the other change this Epic makes to the same commands.
