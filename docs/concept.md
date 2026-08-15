# project-template

**Status:** approved
**Last-reviewed:** 2026-08-15

## Change log

- 2026-08-15 — factual correction: "executes nothing" was untrue of `scripts/init-verify.py`; see [ADR 0003](adr/0003-medium-and-dependencies.md)
- 2026-08-15 — initial write; records what the project becomes once the orchestrator leaves it [[035-orchestrator-own-repo-package]]

## In one paragraph

`project-template` is the scaffold every new project on this machine starts from, and the place the phased workflow itself is developed. It supplies the folder shape, the document templates for each workflow stage, and the Claude Code and CI configuration a fresh repository needs on day one — and it is maintained through the same backlog-and-stages workflow it hands out, so improvements to the workflow are made by using it. There is no product here, no build step and no test runner. Tasks are implemented by an orchestrator that lives in its own repository and is installed once per machine; `project-template`'s part is to make sure that installation is available and that every project it scaffolds says where to find it.

## The problem

Starting a project from nothing means re-deciding the same structure every time: where the backlog lives, what a requirement file looks like, which CI stubs to wire up, what Claude Code is allowed to do without asking. Decided per project, each repository drifts into its own dialect, and an improvement made while working in one of them never reaches the others.

A scaffold answers that, but only for projects created after the improvement lands — because a scaffold ships by copying, and a copy is frozen at the moment it was taken. The orchestrator made this concrete and costly: every `/new-project` run vendored a snapshot of the loop, so a fix made afterwards reached no existing project, and the copies visibly diverged. That is the shape of the problem this project has to keep solving, and the reason it cannot solve it by copying everything.

## The users

- The developer scaffolding a new project, who wants a repository they can start working in immediately rather than one they have to furnish first.
- The developer maintaining the workflow, who needs a single place where a convention can be changed once.
- Claude sessions working inside a scaffolded project, which read the inherited documents to learn how that project is meant to be built.

## What better looks like

`/new-project <name>` produces a repository where `/backlog 001` can be run straight away — the templates, the configuration, and the conventions are already correct, and nothing has to be furnished by hand first.

A convention improved here appears in the next scaffolded project without anyone copying files between repositories.

A session that lands in a scaffolded project can tell from its `CLAUDE.md` alone how tasks get implemented, and where the thing that implements them lives — even though that code is not in the repository it is looking at.

## Scope

### In

- The pristine downstream mirror under `skeleton/` — the exact set of files a fresh project starts with, copied verbatim by `/new-project`.
- Document templates for every stage of the workflow: concept, requirements, architecture decisions, tasks, tests, and the backlog itself.
- Shared configuration that every project should start with: Claude Code permissions, CI stubs, ignore rules, line-ending normalization.
- Ensuring the shared orchestrator installation is available, and that scaffolded projects state where it lives and how to invoke it.
- `project-template`'s own evolution, run through the same backlog and stage sequence it supplies to others.

### Out (for now)

- The orchestrator loop — its code, its test suite, and its specification. It lives in `~/dev/orchestrator`, is installed once per machine, and is used by every project from that one installation. This project's responsibility stops at availability and reference.
- Per-project pinning of the orchestrator version. One shared installation means one version for everyone; that is the chosen property, decided in the orchestrator's `ADR-0003`, not a limitation to be worked around here.
- The workflow skills and slash commands. They live in `~/.claude`, distributed from the `dotfiles-claude` repository, and are shared across every project on the machine rather than inherited per project.
- Being a product, building anything, or running a test suite of its own. The one exception is scaffold-time tooling — a helper invoked from outside to check a project this one just created — which is a narrow permission rather than an open door.
- Retrofitting projects with anything other than the orchestrator change. Once a project is scaffolded it owns its own files; there is no mechanism that pushes later template changes into it.

## Constraints

- Documents, near enough. No build step and nothing to run in order to read what this project supplies — though using it does require Python for the scaffold-time check, and `pip` in the target environment before a scaffolded project can be implemented.
- Three repositories have to stay in agreement and none of them is versioned with the others: this one, `~/dev/orchestrator` for the execution engine, and `dotfiles-claude` for the skills and commands. A change to the scaffold can require a matching change in one of the other two, and nothing enforces that automatically.
- Downstream projects are seeded by copying `skeleton/` verbatim, which means anything that must reach an *already-scaffolded* project cannot travel by that route — it has to be applied to each project, or moved out to something shared.
- Windows-first, with both PowerShell and the Bash tool in use.
