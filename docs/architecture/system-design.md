# System Design

## Overview

`project-template` is a document repository, not a program. It supplies structure — a directory shape, a set of Markdown templates, and configuration files — that new projects start from, and it is maintained through the same workflow it hands out. Nothing in it executes. The load-bearing trade-off, recorded in [ADR 0001](../adr/0001-tech-stack.md), is that anything which must run lives in a sibling repository and is depended on rather than carried: correctness here is established by reading the scaffolded result, not by a test suite.

The one structural idea worth understanding before anything else is the split between `skeleton/` and the repository root. `skeleton/` is a pristine mirror of what a downstream project starts with, copied verbatim; the root is this project's own artefacts, which no downstream project inherits. Every file in the repository is on one side of that line, and which side it is on determines who it belongs to.

---

## Tech Stack

| Layer | Choice | ADR |
|---|---|---|
| Medium | Markdown documents, directory structure, configuration files | 0001 |
| Runtime | None — nothing here executes | 0001 |
| Build / packaging | None | 0001 |
| Test suite | None — verification is by inspection of the scaffolded result | 0001 |
| Task execution | `~/dev/orchestrator`, one shared installation, consumed per its ADR 0003 | 0001 |
| Workflow skills + commands | `dotfiles-claude`, shared across every project on the machine | 0001 |

---

## Component Overview

```
                    ~/.claude  (dotfiles-claude)          ~/dev/orchestrator
                    skills, slash commands                 the loop, installed once
                            │                                      │
                            │ /new-project reads the               │ pip install -e
                            │ scaffold and drives the copy         │ puts `orchestrator`
                            ▼                                      │ on PATH
   ┌────────────────────────────────────────────┐                  │
   │ project-template                           │                  │
   │                                            │                  │
   │  skeleton/          ← copied verbatim ─────┼──────┐           │
   │    CLAUDE.md, README.md, .claude/,         │      │           │
   │    .github/, .gitignore, docs/ templates   │      │           │
   │                                            │      │           │
   │  ── the line ─────────────────────────     │      │           │
   │                                            │      │           │
   │  CLAUDE.md, README.md      ← root only     │      │           │
   │  docs/  concept, backlog, specs,           │      │           │
   │         adr, architecture, tasks, tests    │      │           │
   └────────────────────────────────────────────┘      │           │
                                                       ▼           │
                                        ┌──────────────────────┐   │
                                        │ a downstream project │◄──┘
                                        │  holds no loop code  │  invoked as
                                        │  names it in         │  orchestrator --tasks …
                                        │  CLAUDE.md           │  --project-dir .
                                        └──────────────────────┘
```

The three boxes at the top are separate git repositories. None is versioned with the others, and no commit in any of them describes the whole — see ADR 0001's Consequences.

---

## Key Design Decisions

- **`skeleton/` is copied wholesale, never selectively** — `/new-project` copies `skeleton/.` as a unit, so what a project inherits is decided by what exists in that directory rather than by a list some command has to maintain. Removing a file from the scaffold is the entire mechanism for downstream projects to stop receiving it.
- **Root artefacts mirror the downstream shape** — `docs/backlog/`, `docs/specs/`, `docs/adr/`, `docs/architecture/` at the root have the same structure they have in a scaffolded project, because this project runs its own workflow through them. The templates in `skeleton/docs/` and the real files at the root are the same shape at two stages of life.
- **Nothing reaches a project after it is scaffolded** — there is no update channel from here into an existing project. Anything that must be able to change after the fact has to live outside the scaffold, which is why the orchestrator and the workflow skills are both dependencies rather than copies.
