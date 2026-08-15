# REQ-0004 — `project-template` retains no orchestrator artefacts

**Epic:** E1-orchestrator-extraction
**Status:** active
**Source:** [[035-orchestrator-own-repo-package]]
**Architecture-impact:** none (no ADR)

`project-template` MUST NOT retain the orchestrator's source, its test suite, the build configuration that exists only to run that suite, or the legacy requirements document that describes the loop. Concretely this covers `skeleton/orchestrator/`, `orchestrator-tests/`, `pytest.ini`, and `docs/orchestrator-requirements.md`.

This project's own `CLAUDE.md` and `README.md` MUST NOT describe it as owning, testing, or specifying the loop. Both currently do: `CLAUDE.md` names `skeleton/orchestrator/` "the canonical orchestrator source", lists 164 orchestrator tests under `## Verification`, and documents `pytest` as this project's test command.

## Acceptance

The repository contains no orchestrator module and no test that imports one; `pytest` is no longer documented as a command of this project; and a reader of `CLAUDE.md` and `README.md` finds this project described without any claim to own, verify, or specify the loop.

## Rationale

`REQ-0001` governs what downstream inherits; this one governs what this repository keeps. They are separable — the scaffold can already be clean while the root still holds a test suite for code that lives elsewhere — and the failure of the second is quieter: stale self-description that reads as authority.

The removals are safe and were verified rather than assumed. `skeleton/orchestrator/` and `orchestrator-tests/` were compared file by file against `~/dev/orchestrator` with its suite green at 173 passing: every difference runs the same direction, with the orchestrator repository strictly ahead. `docs/orchestrator-requirements.md` is the one deletion that would have lost something — its prose carries rationale the inline `REQ-NN` tags dropped — so it was preserved verbatim in the orchestrator repository and is tracked there by item `003-legacy-requirements-no-home` before being removed here.

## Related

- [[REQ-0001]] — the same removal on the downstream-facing side of the repository.
