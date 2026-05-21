# project-template

Starter scaffolding for new projects. Combines the phased AI-driven
workflow conventions, Claude Code settings, and the GitHub Actions
stubs that delegate to [mthoatgit/workflows](https://github.com/mthoatgit/workflows).

## Getting Started

### One-time setup (per new repo)

1. Click **"Use this template"** on GitHub → pick a name, clone locally.
2. Add the OAuth secret: **Settings → Secrets and variables → Actions →**
   `CLAUDE_CODE_OAUTH_TOKEN`.
3. Open the project in your IDE with Claude Code installed.
4. Write a project-specific `CLAUDE.md` at the root (code layout,
   stack-specific commands, gotchas). Replace or delete this `README.md`
   once your project is real.

### The phased flow

Each phase ends with explicit user approval before the next begins.
The templates under `docs/` exist as a visible reference for the
expected shape — the `workflow-*` skills fill them in.

| # | Phase | Skill | Where decisions get written | What gets decided |
|---|---|---|---|---|
| 0 | **Concept** | `workflow-concept` | `docs/concept.md` | Problem, users, rough scope, candidate Epics. **No tech.** |
| 1 | **Requirements** | `workflow-requirements` | `docs/specs/README.md` + `docs/specs/epics/E<N>-*.md` | **Tech stack**, Epic list, per-Epic functional & non-functional requirements (stable IDs). |
| 2 | **Architecture** | `workflow-architecture` | `docs/architecture/system-design.md` + `docs/adr/<NNNN>-*.md` | System design, ADRs for non-obvious decisions. |
| 3 | **Tasks** | `workflow-tasks` | `docs/tasks/epics/E<N>/T<NN>-*.md` + `docs/tasks/backlog.md` + Tasks section in each Epic spec | Atomic tasks per Epic, Epic-level acceptance criteria. |
| 4 | **Tests** | `workflow-tests` | `docs/tests/epics/E<N>-*.md` + `strategy.md`, `cross-cutting.md`, `e2e.md` | Test plan and scenarios per Epic. |
| 5 | **Implementation** | `workflow-implementation` | code + commits + PR | One Epic per branch (`epic/<n>-<slug>`), one task per commit, one PR per Epic. |

### Typical first session

```text
/concept "<one-line idea>"        ← Phase 0 — conversational, fills docs/concept.md
... approve ...
(workflow-requirements activates) ← Phase 1 — fills docs/specs/README.md + per-Epic spec files
... approve ...
(workflow-architecture activates) ← Phase 2 — fills system-design.md + ADRs
... approve ...
(workflow-tasks activates)        ← Phase 3 — task files per Epic
... approve ...
(workflow-tests activates)        ← Phase 4 — test scenarios per Epic
... approve ...
/start-epic 1                     ← Phase 5 — implement Epic 1
/ship-epic                        ← Self-review, push, open PR
```

## What's inside

```
.claude/settings.json            Claude Code permissions + model default
.github/workflows/               Stubs delegating to mthoatgit/workflows@v1
.gitignore                       Generic ignores + comment block for stack-specific entries
docs/
  concept.md                     Phase 0 — Concept brief template
  specs/                         Phase 1 — Requirements (Epics + per-Epic specs)
    README.md                    Index template (Goal, Domain, Tech Stack, Epic Index)
    epics/_TEMPLATE.md           Epic spec blueprint (copied per Epic)
    cross-cutting/_TEMPLATE.md   Cross-cutting NFRs blueprint (copied per concern)
  architecture/
    system-design.md             Phase 2 — System design template
  adr/
    README.md                    ADR index template
    _TEMPLATE.md                 ADR blueprint (copied per decision)
  tasks/
    backlog.md                   Phase 3 — Task index template
    epics/_TEMPLATE.md           Task blueprint (copied per task)
  tests/
    README.md                    Phase 4 — Test plan index template
    strategy.md                  Test strategy template
    cross-cutting.md             Cross-cutting tests template
    e2e.md                       End-to-end tests template
    epics/_TEMPLATE.md           Per-Epic test scenarios blueprint
```

## Replacing the placeholders

Every template file contains `<PLACEHOLDER>` markers and a header block
naming the placeholders used in that file. Fill them in (or have a skill
do it) at the start of the corresponding phase.

### Template marker convention

Template files are signalled in two ways:

1. **YAML frontmatter** at the top of the file:
   ```yaml
   ---
   status: template
   ---
   ```
   Machine-readable — skills check this to know the file is still placeholder.
2. **Inline banner** below the title (`> **Template file.** ...`) —
   human-readable, explains how to fill the file in.

**When filling a file with real content, remove BOTH the frontmatter and
the banner.** A file without these markers is considered real content.

Two flavors of template files exist:

| Flavor | Examples | Lifecycle |
|---|---|---|
| **Multi-instance blueprints** (`_TEMPLATE.md`) | `docs/specs/epics/_TEMPLATE.md`, `docs/tasks/epics/_TEMPLATE.md`, `docs/tests/epics/_TEMPLATE.md` | Stay as templates forever. Copied to produce real files (`E1-foo.md`, `T01-bar.md`). The copy inherits the frontmatter; remove it when filling in. |
| **Single-instance placeholders** | `docs/architecture/system-design.md`, `docs/tests/cross-cutting.md`, `docs/specs/README.md`, etc. | One file at the final path with placeholder content. Frontmatter is removed once the file holds real content. |

## Related repositories

- [mthoatgit/workflows](https://github.com/mthoatgit/workflows) —
  reusable GitHub Actions workflows (pinned via `@v1` in the stubs here).
