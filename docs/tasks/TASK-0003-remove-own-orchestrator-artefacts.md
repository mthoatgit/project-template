# TASK-0003 — Remove project-template's own orchestrator artefacts

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0004** — this repository retains no orchestrator source, test suite, build configuration, or legacy requirements document.

## Related ADRs

- **ADR-0001** — commits this project to no runtime code, no test suite, and no build step; these deletions are what make that true rather than aspirational.

## Goal

The repository stops holding a test suite for code that lives elsewhere, and stops holding a specification for a loop it no longer contains.

**Testability:** structural — a Stage 5 spec asserts each path is absent.

## Steps

- Delete `orchestrator-tests/` — twelve modules.
- Delete `pytest.ini`. Its configuration already lives in the orchestrator repository's `pyproject.toml`; nothing is lost.
- Delete `docs/orchestrator-requirements.md`. It is preserved verbatim at `~/dev/orchestrator/docs/backlog/reference/orchestrator-requirements-legacy.md` and tracked there by item `003-legacy-requirements-no-home`. Confirm that copy exists and is byte-identical before deleting.
- Correct the root `.gitignore`: its Python section is introduced by a comment stating *"the orchestrator package itself is Python"*. The rules stay; the justification must go.

## Acceptance Criteria

- The repository MUST contain no test module and no `pytest.ini`.
- `docs/orchestrator-requirements.md` MUST NOT exist here, and the verbatim copy in the orchestrator repository MUST exist and match the deleted file byte for byte.
- No `.gitignore` at either level MUST justify its rules by reference to a bundled orchestrator.
- `pytest` MUST NOT run against this repository, because there is nothing for it to collect.

## Dependencies

- The reference copy in `~/dev/orchestrator` must already be committed. It is — commit `8193151`, filed during this item's Stage 1.
