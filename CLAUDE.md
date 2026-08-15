# project-template

## What this project is

`project-template` is the scaffold every new project on this machine starts from, and the place the phased workflow itself is developed. It supplies structure — a directory shape, document templates, shared configuration — and holds no product, no build step and no test runner. See `docs/concept.md`.

**Dual-nature layout.** Every file is on one side of a line, and which side decides who owns it:

- **`skeleton/`** — what a fresh downstream project starts with. `/new-project` copies `skeleton/.` wholesale and runs `/init-project` fill logic. Treat it as the pristine mirror.
- **Root (`./`)** — project-template's own artefacts: this file, `README.md`, and `docs/` holding its real concept, backlog, REQs, ADRs, tasks and tests about ITSELF.

When editing downstream-facing content, edit under `skeleton/`. When developing project-template itself, the work lives at root — mirroring the folder shape downstream projects use.

## Tech Stack

Authoritative source: `docs/architecture/system-design.md` + `docs/adr/0003-medium-and-dependencies.md`.

| Layer | Choice |
|---|---|
| Medium | Markdown documents, directory structure, configuration files |
| Runtime | None — no product, no build, no runner |
| Build / packaging | None |
| Test suite | None — verification is by inspection |
| Task execution | `~/dev/orchestrator`, installed once per machine |
| Workflow skills + commands | `dotfiles-claude`, shared across every project |

## Commands

There is no build, no test, and no run command. The one executable file is a scaffold-time helper invoked by `/init-project`, never run against this repository:

```bash
python scripts/init-verify.py <target-project-dir>
```

## Verification

Claude MUST establish correctness by inspection, not by a test runner — see `docs/adr/0003-medium-and-dependencies.md`.

- Structural test specs under `docs/tests/` carry runnable `## Verified by` blocks. Claude MUST run the blocks belonging to the work at hand before declaring a task done.
- Procedural specs require a human or a fresh session; Claude MUST NOT mark them verified on its own inference.
- There is no aggregate runner and no merge gate. A structural check fails only when someone runs it — the cost side of ADR-0003, named in its Consequences.

Coverage: `docs/tests/index.md`.

## Dev Environment

- Python 3.11+ on PATH — for `scripts/init-verify.py` and for the orchestrator's installation, not for anything in this repository.
- The orchestrator MUST be installed (`pip install -e ~/dev/orchestrator`) for any project scaffolded from here to be implementable.
- Windows-first; Bash tool and PowerShell both work.

## Code Layout

- `skeleton/` — the downstream mirror. `skeleton/docs/` holds the pristine templates (`_TEMPLATE_*.md`, placeholder files); `skeleton/.claude/`, `skeleton/.github/`, `skeleton/.gitignore` are the shared config every new project inherits.
- `docs/concept.md` — what this project is.
- `docs/backlog/` — project-template's own backlog; `archive/` holds items 001..035.
- `docs/specs/`, `docs/adr/`, `docs/architecture/`, `docs/tasks/`, `docs/tests/` — its own REQs, decisions, system design, work items and test specs.
- `scripts/init-verify.py` — post-write autofix and hard-check for `/init-project`. Runs against a target project at scaffold time.

Full structure: `docs/architecture/system-design.md`.

## Conventions

- Files under `skeleton/` are what downstream projects inherit. Adding one there means every new project gets it from then on.
- Files at root stay here. Downstream projects do NOT inherit them.
- Claude MUST NOT add runtime code, a test suite, or a build step — ADR-0003. Executable tooling MAY exist only as a scaffold-time helper invoked from outside this repository against a target project; `scripts/init-verify.py` is the one such helper. Anything that must execute as part of a product belongs in another repository and is depended on, not carried.

## Gotchas

- Three repositories must stay in agreement and none is versioned with the others: this one, `~/dev/orchestrator`, and `dotfiles-claude` (which is `~/.claude/`, holding skills and commands). Committing here does not commit skill or command edits, and no single commit describes a working whole.
- Nothing reaches a project after it is scaffolded. There is no update channel; anything that must change afterwards has to live outside the scaffold.
- Legacy commits from before the `skeleton/` restructure have `orchestrator/` at the repo root, and commits before Epic 1 have the loop's source in-tree. `git log --follow` preserves history across both moves.

## Implementation

Tasks are executed by the orchestrator. Claude MUST use it during the implementation phase; Claude MUST NOT implement tasks manually.

```bash
orchestrator --tasks docs/tasks/ --project-dir .
```

The orchestrator is **installed, not part of this repository** — its source lives at `~/dev/orchestrator`. See `~/dev/orchestrator/docs/consuming-the-orchestrator.md`.

Epic 1 is the exception and MUST NOT be taken as precedent: it removed this project's test infrastructure, which the orchestrator requires in order to run, so it was implemented manually. Any Epic after it that has no test command has the same problem and MUST resolve it deliberately rather than by repeating the exception — see the `## Implementation note` in `docs/specs/epics/E1-orchestrator-extraction/E1-orchestrator-extraction.md`.
