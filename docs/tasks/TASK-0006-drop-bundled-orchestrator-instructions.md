# TASK-0006 — Drop the bundled-orchestrator instructions from the scaffolding commands

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0006** — the workflow commands do not instruct on a bundled orchestrator.

## Goal

Neither scaffolding command carries instructions about a directory that can no longer exist in any project.

**Testability:** procedural — the change lands in `dotfiles-claude`; a Stage 5 spec verifies the command text and a `/init-project` run against a fresh scaffold.

## Steps

- Edit `~/.claude/commands/init-project.md` — in the separate `dotfiles-claude` repository. Remove step 0, the backwards-compat wipe that runs `rm -rf orchestrator/tests/` and `rm -f pytest.ini`. Renumber the steps that follow, and check whether anything downstream of it refers to step numbers.
- Edit `~/.claude/commands/new-project.md`. Remove the step-6 aside stating the skeleton starts clean with *"no orchestrator tests to remove, no pytest.ini to strip"*. The surrounding sentence about obsolete wipe steps needs rereading — with the orchestrator clause gone, what remains is the backlog-item point, which is still true.
- Leave `/scaffold` alone. Its `python -m orchestrator` invocation resolves from the installed package regardless of working directory and is unaffected by this Epic.
- Leave the six skill files that mention the orchestrator alone. They describe the loop's role in the workflow, not its location.

## Acceptance Criteria

- Neither command's text MUST refer to removing orchestrator files or `pytest.ini` from a scaffolded project.
- `/init-project`'s remaining steps MUST be correctly numbered, and no later text MUST refer to a step number that moved.
- A `/init-project` run against a fresh scaffold MUST perform no orchestrator-related step and MUST otherwise behave as before.
- `/scaffold` MUST be unchanged.

## Dependencies

None. Both passages are already dead text describing a state the scaffold will reach in TASK-0001; removing them earlier or later changes nothing.
